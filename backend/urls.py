from django.urls import path
from .views import UploadAPIView, StatusAPIView, WebhookAPIView, ProductsByRequestAPIView

urlpatterns = [
    path('upload/', UploadAPIView.as_view(), name='upload'),
    path('status/<uuid:request_id>/', StatusAPIView.as_view(), name='status'),
    path('products/<uuid:request_id>/', ProductsByRequestAPIView.as_view(), name='products_by_request'),
    path('webhook/', WebhookAPIView.as_view(), name='webhook'),
]
