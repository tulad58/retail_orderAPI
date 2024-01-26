import jwt
from datetime import datetime, timedelta

from django.conf import settings 
from django.contrib.auth.models import (
	AbstractBaseUser, BaseUserManager, PermissionsMixin
)


from django.db import models



class UserManager(BaseUserManager):
    """
    Django требует, чтобы кастомные пользователи определяли свой собственный
    класс Manager. Унаследовавшись от BaseUserManager, мы получаем много того
    же самого кода, который Django использовал для создания User (для демонстрации).
    """

    def create_user(self, name, email, surname,password=None):
        """ Создает и возвращает пользователя с имэйлом, паролем и именем. """
        if name is None:
            raise TypeError('Users must have a name.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(name=name, surname=surname, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        """ Создает и возввращет пользователя с привилегиями суперадмина. """
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user
    

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(db_index=True, max_length=255, unique=True)
    email = models.EmailField(db_index=True, unique=True)
    surname = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']
    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def token(self):
        return self._generate_jwt_token()

    def get_full_name(self):
        """
        Этот метод требуется Django для таких вещей, как обработка электронной
        почты. Обычно это имя фамилия пользователя, но поскольку мы не
        используем их, будем возвращать username.
        """
        return self.username

    def get_short_name(self):
        """ Аналогично методу get_full_name(). """
        return self.username

    def _generate_jwt_token(self):
        """
        Генерирует веб-токен JSON, в котором хранится идентификатор этого
        пользователя, срок действия токена составляет 1 день от создания
        """
        dt = datetime.now() + timedelta(days=1)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token
        

STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)


class Shop(models.Model):
    name = models.CharField(max_length=50)
    url =  models.URLField(verbose_name="Ссылка", null=True, blank=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = "Список магазинов"


    def __str__(self):
        return self.name
    

class Category(models.Model):
    shop = models.ManyToManyField(Shop, verbose_name="shop_category", related_name="categories")
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.name}"
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Список категорий"
 


class Product(models.Model):
    category = models.ForeignKey(Category, related_name="categories", on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Список продуктов"
  

    def __str__(self):
        return self.name
    

class ProductInfo(models.Model):
    product = models.ForeignKey(Product, 
                            related_name="product_infos", 
                            on_delete=models.CASCADE, 
                            verbose_name="Продукт",
                            blank=True,)
    shop =  models.ForeignKey(Shop, 
                            related_name="product_infos",
                            on_delete=models.CASCADE, 
                            verbose_name="Магазин",
                            blank=True)
    model = models.CharField(max_length=50, blank=True)
    quantity = models.PositiveIntegerField(verbose_name="Колисетсво")
    price = models.PositiveIntegerField(verbose_name="Цена")
    price_rrc = models.PositiveIntegerField(verbose_name="Рекомендуемая розничная цена")
    external_id = models.PositiveIntegerField(verbose_name='Внешний ИД', blank=True)

    class Meta:
        verbose_name = "Информация о прдукте"
        verbose_name_plural = "Список информации о продукте"


    
class Parameter(models.Model):
    name = models.CharField(max_length=60, verbose_name="Название параметра")

    class Meta:
        verbose_name = "Параметр"
        verbose_name_plural = "Список параметров"


    def __str__(self):
        return self.name
    

class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo,
                                on_delete=models.CASCADE,
                                blank=True,
                                verbose_name="Информация о продукте",
                                related_name="product_parameters")
    parameter = models.ForeignKey(Parameter,
                            on_delete=models.CASCADE, 
                            blank=True,
                            verbose_name="Параметр",
                            related_name="product_parameters")
    value = models.CharField(max_length=50, verbose_name="Стоимость")

    class Meta:
        verbose_name = "Продукт и Параметр"
        verbose_name_plural = "Список продуктов и параметров"

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(User, 
                        on_delete=models.CASCADE,
                        related_name="orders",
                        blank=True,
                        verbose_name="Пользователь")
    dt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, verbose_name = "Статус", choices = STATE_CHOICES)

    class Meta:
        verbose_name = "Заказ" 
        verbose_name_plural = "Заказы"

    def __str__(self):
        return self.dt, self.status


class OrderItem(models.Model):
    order = models.ForeignKey(Order, 
                            on_delete=models.CASCADE,
                            blank=True,
                            verbose_name="Заказ",
                            related_name="order_items")
    product = models.ForeignKey(Product, 
                            on_delete=models.CASCADE,
                            blank=True,
                            verbose_name="Продукт",
                            related_name="order_items")
    shop = models.ForeignKey(Shop, 
                            on_delete=models.CASCADE,
                            blank=True,
                            verbose_name="Магазин",
                            related_name="order_items")
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Заказы и продукты"
        verbose_name_plural = "Список заказов и продуктов"

    def __str__(self):
        return self.quantity


class Contact(models.Model):
    type = models.CharField(max_length=50)
    user = models.ForeignKey(User, 
                        on_delete=models.CASCADE,
                        verbose_name="Пользователь",
                        related_name="contacts")
    value = models.CharField(max_length=30, verbose_name="Знчение")

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"
        
    def __str__(self):
        return self.value
