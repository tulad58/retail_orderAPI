from django.urls import path
from .views import CartAPIView, ProductInfoAPIView, upload_products, RegisterAccount, LoginAccount, ShopListAPIView, CategoryListAPIView

app_name = 'app'
urlpatterns = [
    path('products/', upload_products, name="upload"),
    path('user/register/', RegisterAccount.as_view(), name='user-register'),
    path('user/login/', LoginAccount.as_view(), name='user-login'),
    path('productlist/', ProductInfoAPIView.as_view(), name='product-list'),
    path('shops/', ShopListAPIView.as_view(), name='shops'),
    path('categories/', CategoryListAPIView.as_view(), name='categories'),
    path('cart/', CartAPIView.as_view(), name='cart'),
]
