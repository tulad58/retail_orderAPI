from django.urls import include, path, re_path
from .views import upload_products, RegistrationAPIView


urlpatterns = [
    path('products/', upload_products, name="upload"),
    path('users/', RegistrationAPIView.as_view(), name='auth')
]
