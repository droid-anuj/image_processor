from django.contrib import admin
from .models import ProcessingRequest,Product

# Register your models here.
admin.site.register(ProcessingRequest)
admin.site.register(Product)