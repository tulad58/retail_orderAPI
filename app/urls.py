from django.urls import path
from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm
from .views import CartAPIView, ConfirmAccount, ContactAPIView, ProductInfoAPIView, upload_products, RegisterAccount, LoginAccount, ShopListAPIView, CategoryListAPIView

app_name = 'app'
urlpatterns = [
    path('user/register', RegisterAccount.as_view(), name='user-register'),
    path('user/register/confirm', ConfirmAccount.as_view(), name='user-register-confirm'),
    path('user/login', LoginAccount.as_view(), name='user-login'),
    path('user/contact',ContactAPIView.as_view(), name='contact'),
    path('user/password_reset', reset_password_request_token, name='password-reset'),
    path('user/password_reset/confirm', reset_password_confirm, name='password-reset-confirm'),
    path('productlist', ProductInfoAPIView.as_view(), name='product-list'),
    path('products', upload_products, name="upload"),
    path('shops', ShopListAPIView.as_view(), name='shops'),
    path('categories', CategoryListAPIView.as_view(), name='categories'),
    path('cart', CartAPIView.as_view(), name='cart'),
    
]
