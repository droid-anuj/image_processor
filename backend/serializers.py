from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['serial_number', 'product_name', 'input_image_urls', 'output_image_urls']
