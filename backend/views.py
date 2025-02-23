import csv, io
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ProcessingRequest
from django_q.tasks import async_task
from .tasks import process_csv_task

class UploadAPIView(APIView):
    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'CSV file is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            decoded_file = file_obj.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            csv_reader = csv.reader(io_string, delimiter=',')
            header = next(csv_reader)
            expected_header = ['S. No.', 'Product Name', 'Input Image Urls']
            alternate_header = ['Serial Number', 'Product Name', 'Input Image Urls']
            if header != expected_header and header != alternate_header:
                return Response({'error': 'CSV header does not match expected format.'}, 
                              status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'error': 'Invalid CSV file.'}, status=status.HTTP_400_BAD_REQUEST)
        # Create processing request record
        processing_request = ProcessingRequest.objects.create(csv_file=file_obj, status='Pending')
        
        # Trigger asynchronous task using Django-Q
        async_task(process_csv_task, str(processing_request.id))
        return Response({
            'request_id': str(processing_request.id),
            'message': f'Upload successful. Check status at: api/status/{processing_request.id}'
        }, status=status.HTTP_202_ACCEPTED)
    
class StatusAPIView(APIView):
    def get(self, request, request_id):
        try:
            proc_request = ProcessingRequest.objects.get(id=request_id)
        except ProcessingRequest.DoesNotExist:
            return Response({'error': 'Invalid request ID'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'request_id': str(proc_request.id), 'status': proc_request.status})

class WebhookAPIView(APIView):
    def post(self, request):
        # Process incoming webhook data (e.g., log the callback, update status, etc.)
        data = request.data
        # Example: update a request status based on webhook data
        return Response({'status': 'Webhook received'}, status=status.HTTP_200_OK)
