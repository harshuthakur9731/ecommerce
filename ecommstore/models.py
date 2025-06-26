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
    specification = models.JSONField(null=True)
    termsnconditions = models.JSONField(null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    desc1 = models.TextField(null=True)
    image1 = models.ImageField(upload_to = 'static', blank=True, null=True)
    image2 = models.ImageField(upload_to = 'static', blank=True, null=True)
    image3 = models.ImageField(upload_to = 'static', blank=True, null=True)

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant_name = models.CharField(max_length=255)

    def __str__ (self):
        return self.variant_name

class Order(models.Model):
    status_choices = [
        ('created','created'),('placed','placed'),('shipped','shipped'),('delivered','delivered')
    ]
    order_id = models.CharField(max_length=12,primary_key=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2,max_digits=11,default=0)
    status = models.CharField(max_length=15,choices=status_choices,default='created')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_id

class OrderItem(models.Model):
    order = models.ForeignKey(Order,related_name='items',on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    unitprice = models.DecimalField(decimal_places=2,max_digits=11,default=0)
    amount = models.DecimalField(decimal_places=2,max_digits=11,default=0)
    quantity = models.IntegerField()

    def __str__(self):
        return f'{self.quantity} of {self.product.name}'

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.PositiveIntegerField(default=1)
    amount = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product', 'variant')  # Prevent duplicate items in cart
    
    def save(self, *args, **kwargs):
        # Calculate total_price before saving
        if self.quantity is not None and self.price is not None:
            self.amount = self.quantity * self.price
        super().save(*args, **kwargs) 

    def __str__(self):
        return f"{self.quantity}x {self.product.name} for {self.user.username}"

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    address = models.TextField()
    profile_picture = models.ImageField(upload_to='static', blank=True, null=True)

    def __str__(self):
        return self.user.username


