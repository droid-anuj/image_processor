import requests
from PIL import Image
from io import BytesIO
from .models import ProcessingRequest, Product

def process_csv_task(request_id):
    try:
        proc_request = ProcessingRequest.objects.get(id=request_id)
        proc_request.status = 'Processing'
        proc_request.save()
        products = Product.objects.filter(processing_request=proc_request)
        for product in products:
            input_urls = product.input_image_urls.split(',')
            output_urls = []
            for url in input_urls:
                try:
                    # url = url.strip()
                    # Download the image
                    
                    # response = requests.get(url)
                    # img = Image.open(BytesIO(response.content))
                    # buffer = BytesIO()
                    # img.save(buffer, format='JPEG', quality=50)
                    
                    # Modify URL to insert 'compressed' before the filename
                    # Upload the compressed image to a storage service (e.g., AWS S3)
                    # this need to implement this part
                    
                    url_parts = url.rsplit('/', 1)
                    if len(url_parts) == 2:
                        processed_image_url = f"{url_parts[0]}/compressed/{url_parts[1]}"
                        processed_image_url = processed_image_url.replace('.jpg', '_compressed.jpg')
                    else:
                        processed_image_url = url.replace('.jpg', '_compressed.jpg')
                    
                    output_urls.append(processed_image_url)
                except Exception:
                    output_urls.append('Error processing image')

            # Update processed image URLs
            product.output_image_urls = ','.join(output_urls)
            product.save()
        proc_request.status = 'Completed'
        proc_request.save()
    except Exception:
        proc_request.status = 'Failed'
        proc_request.save()
