import csv
import io
import requests
from .models import ProcessingRequest, Product
from PIL import Image
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

def process_csv_task(request_id):
    try:
        logger.info(f"Processing request started: {request_id}")
        proc_request = ProcessingRequest.objects.get(id=request_id)
        proc_request.status = 'Processing'
        proc_request.save()

        # Open and read the CSV file
        csv_file = proc_request.csv_file
        csv_file.open('r')

        decoded_file = csv_file.read()  # Ensure this returns a string
        if isinstance(decoded_file, bytes):
            logger.warning("CSV file returned bytes instead of a string. Decoding manually.")
            decoded_file = decoded_file.decode('utf-8')

        io_string = io.StringIO(decoded_file)
        reader = csv.reader(io_string, delimiter=',')
        
        header = next(reader, None)
        if not header:
            raise ValueError("CSV file is empty or missing a header")

        for row in reader:
            try:
                if len(row) < 3:
                    logger.error(f"Malformed CSV row (Expected 3 columns, got {len(row)}): {row}")
                    continue

                serial, product_name, input_image_urls = row[0], row[1], row[2]
                logger.info(f"Processing product: Serial={serial}, Name={product_name}")

                product = Product.objects.create(
                    processing_request=proc_request,
                    product_name=product_name,
                    input_image_urls=input_image_urls
                )

                urls = [url.strip() for url in input_image_urls.split(',') if url.strip()]
                output_urls = []

                for url in urls:
                    try:
                        logger.info(f"Downloading image: {url}")
                        response = requests.get(url)
                        response.raise_for_status()

                        img = Image.open(BytesIO(response.content))
                        buffer = BytesIO()
                        img.save(buffer, format='JPEG', quality=50)

                        # Insert '/compressed' before the filename in the URL
                        url_parts = url.rsplit('/', 1)
                        processed_image_url = f"{url_parts[0]}/compressed/{url_parts[1]}"
                        processed_image_url = processed_image_url.replace('.jpg', '_compressed.jpg')
                        output_urls.append(processed_image_url)
                        logger.info(f"Image processed successfully: {processed_image_url}")
                    except requests.RequestException as e:
                        logger.error(f"Failed to download image {url}: {e}")
                        output_urls.append('Error downloading image')

                    except Exception as e:
                        logger.error(f"Error processing image {url}: {e}")
                        output_urls.append('Error processing image')

                product.output_image_urls = ','.join(output_urls)
                product.save()

            except IndexError:
                logger.error(f"Malformed CSV row: {row}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error processing row {row}: {e}")
                continue

        proc_request.status = 'Completed'
        proc_request.save()
        logger.info(f"Processing request {request_id} completed successfully.")

        # Trigger webhook if provided
        if proc_request.webhook_url:
            try:
                response = requests.post(proc_request.webhook_url, json={'request_id': request_id, 'status': proc_request.status})
                response.raise_for_status()
                logger.info(f"Webhook triggered successfully: {proc_request.webhook_url}")
            except requests.RequestException as e:
                logger.error(f"Failed to send webhook: {e}")

    except ProcessingRequest.DoesNotExist:
        logger.error(f"ProcessingRequest with ID {request_id} not found.")
    except Exception as e:
        logger.error(f"Critical failure in process_csv_task: {e}")
        proc_request.status = 'Failed'
        proc_request.save()
