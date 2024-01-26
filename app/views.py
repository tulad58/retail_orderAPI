import requests

from django.shortcuts import render, redirect
from django.conf import settings


from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.viewsets import ModelViewSet
from rest_framework import status

from yaml import load as load_yaml, Loader
from .models import Shop, Category, Contact, Order, OrderItem, Parameter, Product, ProductInfo, ProductParameter, User

from .serializers import RegistrationSerializer


class RegistrationAPIView(APIView):
    """
    Разрешить всем пользователям (аутентифицированным и нет) доступ к данному эндпоинту.
    """
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

def upload_products(request):
    if request.method == 'POST':
        try:
            file = request.FILES['myfile']
            data = load_yaml(file, Loader=Loader)

            shop, _ = Shop.objects.get_or_create(
                name=data.get('shop'),
                url=data.get('url', '')
            )

            for category in data.get('categories', []):
                category_object, _ = Category.objects.get_or_create(
                    name=category.get('name')
                )
            category_object.shop.add(shop)    

            for item in data.get('goods', []):
                product_object, _ = Product.objects.get_or_create(
                    name=item.get('name'),
                    category=category_object
                )

                product_info_object = ProductInfo.objects.create(
                    product=product_object,
                    external_id=item.get('id'),
                    model=item.get('model'),
                    price=item.get('price'),
                    price_rrc=item.get('price_rrc'),
                    quantity=item.get('quantity'),
                    shop=shop
                )

                for key, value in item.get('parameters', {}).items():
                    parameter_object, _ = Parameter.objects.get_or_create(name=key)
                    ProductParameter.objects.create(
                        product_info=product_info_object,
                        parameter=parameter_object,
                        value=value
                    )

            print('Ok')
            return redirect('/')

        except Exception as e:
            print(f'Error: {e}')

    return render(request, 'simple_upload.html')