from django.http import JsonResponse
from requests import request

from django.conf import settings
from django.shortcuts import render, redirect
from django.db.models import Q, Sum, F, Prefetch
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate, logout
from django.db import IntegrityError

from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.request import Request 

from .models import Shop, Category, Contact, Order, OrderItem, Parameter, Product, ProductInfo, ProductParameter, User

from .serializers import CategorySerializer, ContactSerializer, OrderItemSerializer, OrderSerializer, ProductInfoSerializer, ShopSerializer, UserSerializer

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
            return JsonResponse({'status': False, 'Error':'Log in required'}, status=403)
        print(request.user.id)
        queryset = Order.objects.filter(user=request.user.id, state='basket').prefetch_related(
            Prefetch('order_items__product_info__product__category', queryset=Category.objects.all()),
            Prefetch('order_items__product_info__product_parameters__parameter', queryset=Parameter.objects.all()),
            ).annotate(
            total_sum=Sum(F('order_items__quantity') * F('order_items__product__price'))).distinct()
        serializer = OrderSerializer(queryset, many=True)
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
            order, status = Order.objects.get_or_create(user=request.user.id, state='basket')
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

    def delete(self, request, *args, **kwargs):
        """
                Remove  items from the user's basket.

                Args:
                - request (Request): The Django request object.

                Returns:
                - JsonResponse: The response indicating the status of the operation and any errors.
                """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('items')
        if items_sting:
            items_list = items_sting.split(',')
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
            query = Q()
            objects_deleted = False
            for order_item_id in items_list:
                if order_item_id.isdigit():
                    query = query | Q(order_id=basket.id, id=order_item_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = OrderItem.objects.filter(query).delete()[0]
                return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})    

    def put(self, request, *args, **kwargs):
        """
               Update the items in the user's basket.

               Args:
               - request (Request): The Django request object.

               Returns:
               - JsonResponse: The response indicating the status of the operation and any errors.
               """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('items')
        if items_sting:
            try:
                items_dict = load_json(items_sting)
            except ValueError:
                return JsonResponse({'Status': False, 'Errors': 'Неверный формат запроса'})
            else:
                basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
                objects_updated = 0
                for order_item in items_dict:
                    if type(order_item['id']) == int and type(order_item['quantity']) == int:
                        objects_updated += OrderItem.objects.filter(order_id=basket.id, id=order_item['id']).update(
                            quantity=order_item['quantity'])

                return JsonResponse({'Status': True, 'Обновлено объектов': objects_updated})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class ContactAPIView(APIView):
    def get(self, request, *args, **kwargs):
        """
               Retrieve the contact information of the authenticated user.

               Args:
               - request (Request): The Django request object.

               Returns:
               - Response: The response containing the contact information.
        """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        contact = Contact.objects.filter(
            user_id=request.user.id)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error':'Log in required'}, status=403)
        if {'city', 'street', 'phone'}.issubset(request.data):
            request.data._mutable = True
            request.data.update({'user': request.user.id})
            serializer = ContactSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({'Status': False, 'Errors': serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}) 

    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            """
                Update the contact information of the authenticated user.

                Args:
                - request (Request): The Django request object.

                Returns:
                - JsonResponse: The response indicating the status of the operation and any errors.
                """
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if 'id' in request.data:
            if request.data['id'].isdigit():
                contact = Contact.objects.filter(id=request.data['id'], user_id=request.user.id).first()
                print(contact)
                if contact:
                    serializer = ContactSerializer(contact, data=request.data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return JsonResponse({'Status': True})
                    else:
                        return JsonResponse({'Status': False, 'Errors': serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_sting = request.data.get('items')
        if items_sting:
            items_list = items_sting.split(',')
            query = Q()
            objects_deleted = False
            for contact_id in items_list:
                if contact_id.isdigit():
                    query = query | Q(user_id=request.user.id, id=contact_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = Contact.objects.filter(query).delete()[0]
                return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

def upload_products(request):
    """
        Upload yaml files to db
    """
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
