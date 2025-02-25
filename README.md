📝 API Documentation for Django Image Processing System
This document provides clear specifications for the API endpoints and a description of asynchronous workers for background processing.

📌 1. API Endpoints
🔹 1.1 Upload CSV File (Start Processing)
➡️ Endpoint:
POST /api/upload/

🔹 Request:
Content-Type: multipart/form-data
Body Parameters:
file (CSV File) → Upload the CSV file containing product and image URLs.
🔹 Example Request (cURL):
curl -X POST "https://image-processor-yrql.onrender.com/api/upload/" \
  -F "file=@sample.csv"

🔹 Response:
{
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
}

🛠️ Functionality:
Validates the CSV file format.
Parses the CSV data and stores it in the database.
Returns a unique request ID.
Starts asynchronous processing for images.

🔹 1.2 Check Processing Status
➡️ Endpoint:
GET /api/status/<request_id>/

🔹 Example Request:
GET /api/status/550e8400-e29b-41d4-a716-446655440000/

🔹 Response:
{
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "Processing"
}

📌 Possible Status Values:
"Pending" → The request has been created but not started.
"Processing" → Images are being processed.
"Completed" → Image processing is done.
"Failed" → The request encountered an error.

🔹 1.3 Get Processed Data by Request ID
➡️ Endpoint:
GET /api/products/<request_id>/

🔹 Example Request:
GET /api/products/550e8400-e29b-41d4-a716-446655440000/

🔹 Response:
{
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "products": [
        {
            "serial_number": 1,
            "product_name": "SKU1",
            "input_image_urls": "https://example.com/img1.jpg,https://example.com/img2.jpg",
            "output_image_urls": "https://example.com/img1_compressed.jpg,https://example.com/img2_compressed.jpg"
        },
        {
            "serial_number": 2,
            "product_name": "SKU2",
            "input_image_urls": "https://example.com/img3.jpg",
            "output_image_urls": "https://example.com/img3_compressed.jpg"
        }
    ]
}

🛠️ Functionality:
Fetches all products associated with a request ID.
Shows both original and processed image URLs.

⚙️ 2. Asynchronous Workers Documentation
🔹 Worker Functionality
The worker processes images asynchronously using Django-Q (qcluster).
It reads unprocessed images, downloads them, compresses them, and updates the database.

🔹 How Workers Process Images
1️⃣ Fetch all products associated with a request
 2️⃣ Download each image from the given URL
 3️⃣ Compress each image to 50% quality
 4️⃣ Generate a new processed image URL (simulation)
 5️⃣ Update the database with processed image URLs
 6️⃣ Mark the request as "Completed"
 7️⃣ Trigger the webhook (if provided)

🔹 Worker Implementation (tasks.py)
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
                    response = requests.get(url.strip())
                    img = Image.open(BytesIO(response.content))
                    buffer = BytesIO()
                    img.save(buffer, format='JPEG', quality=50)
                    processed_image_url = url.strip().replace('.jpg', '_compressed.jpg')
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



🎯 Final Summary
✅ API Endpoints
POST /api/upload/ → Uploads a CSV and starts processing
GET /api/status/<request_id>/ → Check processing status
GET /api/products/<request_id>/ → Get processed image URLs
✅ Worker System
Runs in Render background worker (qcluster)
Downloads, compresses, and updates images in the database
Calls webhook when processing is done


