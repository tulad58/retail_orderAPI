from django.urls import path
from .views import simple_upload, upload_products

urlpatterns = [
    path('', simple_upload, name="upload"),
    path('products/', upload_products, name="upload")
]
