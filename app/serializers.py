from rest_framework import serializers
from .models import Product, User


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class RegistrationSerializer(serializers.ModelSerializer):
    """ Сериализация регистрации пользователя и создания нового. """

    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )
    token = serializers.CharField(max_length=255, read_only=True)
    name = serializers.CharField(max_length=50)
    surname = serializers.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['email', 'name','surname', 'password', 'token' ]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
