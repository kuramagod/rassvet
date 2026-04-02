from django.db import models
from django.urls import reverse
import slugify
import uuid


def generate_code():
        return f"REQ-{str(uuid.uuid4())[:8]}"


class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    description = models.TextField()
    short_description = models.TextField(max_length=120)
    image = models.ImageField(upload_to="static/images/products")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):  
        return reverse('product', kwargs={'product_slug': self.slug})

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductCharacteristic(models.Model):
    name = models.CharField(max_length=120)
    value = models.CharField(max_length=120)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="characteristics")

    def __str__(self):
        return f"{self.product.name}: {self.name} {self.value}"
    
    class Meta:
        verbose_name = "Характеристика товара"
        verbose_name_plural = "Характеристики товаров"


class ProductImages(models.Model):
    image = models.ImageField(upload_to="static/images/products")
    is_main = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"


class DeliveryType(models.Model):
    name = models.CharField(max_length=220)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Тип доставки"
        verbose_name_plural =  "Типы доставок"
    

class RequestStatus(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=120)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Статус запроса"
        verbose_name_plural = "Статус запросов"


class Client(models.Model):
    company_name = models.CharField(max_length=200)
    tin = models.CharField(max_length=12)
    legal_address = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name
    
    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"


class Contact(models.Model):
    fullname = models.CharField(max_length=220)
    jobtitle = models.CharField(max_length=220)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=120)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="contacts")

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"

    def __str__(self):
        return f"{self.fullname} {self.jobtitle} компании {self.client.company_name}"


class Request(models.Model):
    code = models.CharField(max_length=50, unique=True, editable=False, default=generate_code)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="requests")
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="requests")
    status = models.ForeignKey(RequestStatus, on_delete=models.CASCADE, related_name="requests")
    delivery_type = models.ForeignKey(DeliveryType, on_delete=models.CASCADE, related_name="requests")
    delivery_address = models.CharField(max_length=220)
    comment = models.CharField(max_length=200, null=False, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_total(self):
        return sum(item.price * item.quantity for item in self.items.all())

    def __str__(self):
        return self.code
    
    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"


class RequestItem(models.Model):
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="items")

    def __str__(self):
        return f"Заказ {self.request}: {self.product}"
    
    class Meta:
        verbose_name = "Товар заявки"
        verbose_name_plural = "Товары заявок"


class Message(models.Model):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, )
    email = models.EmailField(max_length=120)
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"


class News(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(max_length=550)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="static/images/news")

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Новости"
        verbose_name_plural = "Новости"