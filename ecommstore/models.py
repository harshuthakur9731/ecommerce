from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Product(models.Model):
    product_code = models.CharField(max_length=12,primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to = 'static', blank=True, null=True)
    price = models.DecimalField(max_digits=12,decimal_places=2)
    stock = models.IntegerField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    order_id = models.CharField(max_length=12,primary_key=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order {self.id} by {self.user.username}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order,related_name='items',on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f'{self.quantity} of {self.product.name}'

class Customer(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    address = models.TextField()

    def __str__(self):
        return self.user.username

