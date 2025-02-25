import csv, io
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ProcessingRequest , Product
from django_q.tasks import async_task
from .tasks import process_csv_task
from .serializers import ProductSerializer
# Configure logger
logger = logging.getLogger(__name__)

class UploadAPIView(APIView):
    def post(self, request):
        logger.info("Received a new file upload request.")

        file_obj = request.FILES.get('file')
        if not file_obj:
            logger.error("No CSV file provided in the request.")
            return Response({'error': 'CSV file is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Read and decode the uploaded CSV file
            decoded_file = file_obj.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            csv_reader = csv.reader(io_string, delimiter=',')

            # Validate CSV header
            header = next(csv_reader, None)
            expected_header = ['Serial Number', 'Product Name', 'Input Image Urls']
            alternate_header = ['S. No.', 'Product Name', 'Input Image Urls']

            if header not in [expected_header, alternate_header]:
                logger.error(f"Invalid CSV header: {header}")
                return Response({
                    'error': 'CSV header does not match expected format. First column should be "Serial Number" or "S. No."'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create a new Processing Request
            processing_request = ProcessingRequest.objects.create(status='Pending')
            logger.info(f"Created ProcessingRequest with ID: {processing_request.id}")

            # Store each row as a Product entry
            for row in csv_reader:
                try:
                    serial, product_name, input_image_urls = row[0], row[1], row[2]
                    product = Product.objects.create(
                        processing_request=processing_request,
                        serial_number=int(serial),
                        product_name=product_name,
                        input_image_urls=input_image_urls
                    )
                    logger.info(f"Stored product: {product_name} (Serial: {serial})")
                except Exception as row_error:
                    logger.error(f"Error processing row {row}: {row_error}")
                    continue

            # Start background processing
            process_csv_task(str(processing_request.id))
            logger.info(f"Processing task started for request ID: {processing_request.id}")

            return Response({'request_id': str(processing_request.id)}, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            logger.exception(f"Unexpected error during file processing: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
class StatusAPIView(APIView):
    def get(self, request, request_id):
        try:
            proc_request = ProcessingRequest.objects.get(id=request_id)
        except ProcessingRequest.DoesNotExist:
            return Response({'error': 'Invalid request ID'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'request_id': str(proc_request.id), 'status': proc_request.status})

class ProductsByRequestAPIView(APIView):
    def get(self, request, request_id):
        try:
            proc_request = ProcessingRequest.objects.get(id=request_id)
            products = Product.objects.filter(processing_request=proc_request)

            # Serialize the data
            serializer = ProductSerializer(products, many=True)
            return Response({'request_id': request_id, 'products': serializer.data}, status=status.HTTP_200_OK)

        except ProcessingRequest.DoesNotExist:
            return Response({'error': 'Invalid request ID'}, status=status.HTTP_404_NOT_FOUND)
        
class WebhookAPIView(APIView):
    def post(self, request):
        # Process incoming webhook data (e.g., log the callback, update status, etc.)
        data = request.data
        # Example: update a request status based on webhook data
        return Response({'status': 'Webhook received'}, status=status.HTTP_200_OK)
