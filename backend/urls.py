from django.urls import path
from .views import UploadAPIView, StatusAPIView, WebhookAPIView

urlpatterns = [
    path('upload/', UploadAPIView.as_view(), name='upload'),
    path('status/<uuid:request_id>/', StatusAPIView.as_view(), name='status'),
    path('webhook/', WebhookAPIView.as_view(), name='webhook'),
]
