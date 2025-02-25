import uuid
from django.db import models

class ProcessingRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=20, default='Pending') 
    created_at = models.DateTimeField(auto_now_add=True)
    # webhook_url = models.URLField(blank=True, null=True)  

class Product(models.Model):
    processing_request = models.ForeignKey(ProcessingRequest, related_name='products', on_delete=models.CASCADE)
    serial_number = models.IntegerField(default=0)
    product_name = models.CharField(max_length=255, default='Untitled Product')
    input_image_urls = models.TextField(default='')  
    output_image_urls = models.TextField(blank=True, null=True, default='')
