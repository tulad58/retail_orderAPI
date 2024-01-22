from django.db import models
from django.contrib.auth.models import User



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
