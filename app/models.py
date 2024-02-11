from django.conf import settings 
from django.contrib.auth.models import (
	AbstractUser, BaseUserManager, PermissionsMixin
)
from django.contrib.auth import validators
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator


STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)

USER_TYPE_CHOICES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'),

)


class UserManager(BaseUserManager):
    """
    Миксин для управления пользователями
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)
    

class User(AbstractUser):
    """
    Стандартная модель пользователей
    """
    REQUIRED_FIELDS = []
    objects = UserManager()
    USERNAME_FIELD = 'email'
    email = models.EmailField(_('email address'), unique=True)
    company = models.CharField(verbose_name='Компания', max_length=40, blank=True)
    position = models.CharField(verbose_name='Должность', max_length=40, blank=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    type = models.CharField(verbose_name='Тип пользователя', choices=USER_TYPE_CHOICES, max_length=5, default='buyer')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Список пользователей"
        ordering = ('email',)
     

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
                            related_name="product_info", 
                            on_delete=models.CASCADE, 
                            verbose_name="Продукт",
                            blank=True,)
    shop =  models.ForeignKey(Shop, 
                            related_name="product_info",
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
    objects = models.manager.Manager()
    user = models.ForeignKey(User, 
                        on_delete=models.CASCADE,
                        related_name="orders",
                        blank=True,
                        verbose_name="Пользователь")
    dt = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=50, verbose_name = "Статус", choices = STATE_CHOICES)
    contact = models.ForeignKey('Contact', verbose_name='Контакт',
                                blank=True, null=True,
                                on_delete=models.CASCADE)
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
                            related_name="ordered_items")
    product = models.ForeignKey(ProductInfo, 
                            on_delete=models.CASCADE,
                            blank=True,
                            verbose_name="Продукт",
                            related_name="ordered_items")
    shop = models.ForeignKey(Shop, 
                            on_delete=models.CASCADE,
                            blank=True,
                            verbose_name="Магазин",
                            related_name="ordered_items")
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Заказы и продукты"
        verbose_name_plural = "Список заказов и продуктов"

    def __str__(self):
        return self.quantity


class Contact(models.Model):
    objects = models.manager.Manager()
    user = models.ForeignKey(User, verbose_name='Пользователь',
                             related_name='contacts', blank=True,
                             on_delete=models.CASCADE)

    city = models.CharField(max_length=50, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house = models.CharField(max_length=15, verbose_name='Дом', blank=True)
    structure = models.CharField(max_length=15, verbose_name='Корпус', blank=True)
    building = models.CharField(max_length=15, verbose_name='Строение', blank=True)
    apartment = models.CharField(max_length=15, verbose_name='Квартира', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон')

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = "Список контактов пользователя"

    def __str__(self):
        return f'{self.city} {self.street} {self.house}'
