from django.urls import path
from .views import simple_upload

urlpatterns = [
    path('', simple_upload, name="upload")
]
