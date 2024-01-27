from django.urls import include, path, re_path
from .views import upload_products, RegisterAccount, LoginAccount

app_name = 'app'
urlpatterns = [
    path('products/', upload_products, name="upload"),
    path('user/register/', RegisterAccount.as_view(), name='user-register'),
    path('user/login/', LoginAccount.as_view(), name='user-login')
]
