import uuid
from django.db import models

class ProcessingRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    csv_file = models.FileField(upload_to='uploads/')
    status = models.CharField(max_length=20, default='Pending')  # e.g., Pending, Processing, Completed, Failed
    created_at = models.DateTimeField(auto_now_add=True)
    # Optional webhook callback URL
    webhook_url = models.URLField(blank=True, null=True)

class Product(models.Model):
    processing_request = models.ForeignKey(ProcessingRequest, related_name='products', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    input_image_urls = models.TextField()  # comma separated list of URLs
    output_image_urls = models.TextField(blank=True, null=True)  # comma separated processed image URLs
