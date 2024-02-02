from django.http import JsonResponse
from requests import request

from django.shortcuts import render, redirect
from django.conf import settings
from django.db.models import Q, Sum, F
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate, logout
from django.db import IntegrityError

from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.request import Request 

from .models import Shop, Category, Contact, Order, OrderItem, Parameter, Product, ProductInfo, ProductParameter, User

from .serializers import CategorySerializer, OrderItemSerializer, OrderSerializer, ProductInfoSerializer, ShopSerializer, UserSerializer

from ujson import loads as load_json
from yaml import load as load_yaml, Loader

class RegisterAccount(APIView):
    """
    Для регистрации покупателей
    """
    def post(self, request, *args, **kwargs):
        """
            Process a POST request and create a new user.

            Args:
                request (Request): The Django request object.

            Returns:
                JsonResponse: The response indicating the status of the operation and any errors.
            """
        if {'first_name', 'last_name', 'email', 'password'}.issubset(request.data):
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
            else:
                user_serializer = UserSerializer(data=request.data)
                if user_serializer.is_valid():
                    user = user_serializer.save()
                    user.set_password(request.data['password'])
                    user.save()
                    return JsonResponse({'Status': True})
                else:
                    return JsonResponse({'Status': False, 'Errors': user_serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})



class LoginAccount(APIView):
    """
    Класс для авторизации пользователей
    """

    # Авторизация методом POST
    def post(self, request, *args, **kwargs):
        """
                Authenticate a user.

                Args:
                    request (Request): The Django request object.

                Returns:
                    JsonResponse: The response indicating the status of the operation and any errors.
                """
        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['email'], password=request.data['password'])
            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)

                    return JsonResponse({'Status': True, 'Token': token.key})

            return JsonResponse({'Status': False, 'Errors': 'Не удалось авторизовать'})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class LogOutAPIView(APIView):
    def logut(self, request):
        logout(request)


class CategoryListAPIView(generics.ListAPIView):
    """
    Класс для просмотра категорий
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShopListAPIView(generics.ListAPIView):
    """
    Класс для просмотра магазинов
    """
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


class ProductInfoAPIView(APIView):       
    """
    Класс фильтрации продуктов и категорий
    """
    def get(self, request, format=None):
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')
        query = Q(shop_id=shop_id) | Q(product__category_id=category_id)
        queryset = ProductInfo.objects.filter(
            query
            ).select_related(
        'shop', 'product__category').prefetch_related(
        'product_parameters__parameter').distinct()
        serializer = ProductInfoSerializer(queryset, many=True)

        return Response(serializer.data)

class CartAPIView(APIView):
    """
    Корзина с возможностью добавления и удаления товаров
    Список товаров с полями

    - Наименование товара
    - Магазин
    - Цена
    - Количество
    - Сумма

    A class for managing the user's shopping basket.

    Methods:
    - get: Retrieve the items in the user's basket.
    - post: Add an item to the user's basket.
    - put: Update the quantity of an item in the user's basket.
    - delete: Remove an item from the user's basket.

    Attributes:
    - None
    """

    # получить корзину
    def get(self, request, *args, **kwargs):
        """
                Retrieve the items in the user's basket.

                Args:
                - request (Request): The Django request object.

                Returns:
                - Response: The response containing the items in the user's basket.
                """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        basket = Order.objects.filter(
            user_id=request.user.id, state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        """
        Add an items to the user's basket.

        Args:
        - request (Request): The Django request object.

        Returns:
        - JsonResponse: The response indicating the status of the operation and any errors.
        """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items = request.data.get('items')
        if items:
            try:
                items_dict = load_json(items)
            except ValueError:
                JsonResponse({'status': False, 'errors': 'Неверный формат запроса'})
            order, status = Order.objects.get_or_create(user=request.user.id, status='basket')
            objects_created = 0
            for order_item in items_dict:
                order_item.update({'order': order.id})
                serializer = OrderItemSerializer(data=order_item)
                if serializer.is_valid():
                    try:
                        serializer.save()
                    except InterruptedError as error:
                        return JsonResponse({'status': 'False', 'error': str(error)})
                    else:
                        objects_created += 1
                else:
                    return JsonResponse({'status': 'false', 'errors': serializer.errors})
            return JsonResponse({'status': True, 'объектов создано': objects_created})    
        return JsonResponse({'status': False, 'errors': 'Не указаны все необходимые аргументы'})    


    def put(self, request):
        user = request.user.id
        user_obj = User.objects.get(id=user)
        order = Order.objects.create(user=user_obj, status='new')
        product_obj = Product.objects.get(id=request.data.get('product'))
        shop_obj = Shop.objects.get(id=request.data.get('shop'))
        order_items = OrderItem.objects.create(
            order=order,
            product=product_obj,
            shop=shop_obj,
            quantity=request.data.get('quantity'),
        )


        return Response(user)
        
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
