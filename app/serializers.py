from rest_framework import serializers
from .models import Product, User, Category, Shop, ProductInfo, ProductParameter, OrderItem, Order, Contact, Parameter


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'url')
        read_only_fields = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    shop = ShopSerializer()
    class Meta:
        model = Category
        fields = ('id', 'shop', 'name')
        read_only_fields = ('id',)


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = Product
        fields = ('id', 'category', 'name',)
        read_only_fields = ('id',)        
        

class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer() 
    shop = ShopSerializer()
    class Meta:
        model = ProductInfo
        fields = ('id', 'product', 'shop', 'model', 'quantity', 'price', 'price_rrc', 'external_id')
        read_only_fields = ('id',)


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'user', 'phone')
        read_only_fields = ('id',)
        extra_kwargs = {
            'user': {'write_only': True}
        }

class UserSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'company', 'position', 'contacts')
        read_only_fields = ('id',)


class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ('id', 'name')
        read_only_fields = ('id',)


class ProductParameterSerialezer(serializers.Serializer):
    product_info = ProductInfoSerializer(read_only=True)
    parameter = ParameterSerializer(read_only=True, many=True)
    class Meta:
        model = ProductParameter
        fields = ('id', 'product_info', 'parameter', 'value')
        read_only_fields = ('id',)


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Order
        fields = ('id', 'user', 'dt', 'status')
        read_only_fields = ('id',)


class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer()
    product = ProductSerializer()
    shop = ShopSerializer()
    class Meta:
        model = OrderItem
        fields = ('id', 'order', 'product', 'shop', 'quantity')
        read_only_fields = ('id',)


class ContactSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Contact
        fields = ('id', 'type', 'user', 'value')
        read_only_fields = ('id',)
        