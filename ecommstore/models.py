from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Product(models.Model):
    product_code = models.CharField(max_length=12, primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=30)
    image = models.ImageField(
        upload_to="products/", blank=True, null=True
    )
    price = models.DecimalField(max_digits=12, decimal_places=2,default=0)
    stock = models.PositiveIntegerField(default=0)
    specification = models.JSONField(null=True)
    termsnconditions = models.JSONField(null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    desc1 = models.TextField(null=True)
    is_returnable = models.BooleanField(default=True,help_text="Allow customers to return this product.")

    image1 = models.ImageField(
        upload_to="products/", blank=True, null=True
    )
    image2 = models.ImageField(
        upload_to="products/", blank=True, null=True
    )
    image3 = models.ImageField(
        upload_to="products/", blank=True, null=True
    )

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name="variants")
    variant_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2,default=0)
    image = models.ImageField(
        upload_to="products/", blank=True, null=True
    )
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.variant_name}"

    class Meta:
        unique_together = ("product", "variant_name")

class Order(models.Model):
    status_choices = [
        ('created','created'),('placed','placed'),('shipped','shipped'),('delivered','delivered'),('cancelled','cancelled')
    ]
    order_id = models.CharField(max_length=36, primary_key=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2,max_digits=11,default=0)
    status = models.CharField(max_length=15,choices=status_choices,default='created')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now_add=True)
    delivery_address = models.TextField(blank=True, default="")
    subtotal = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    shipping_charge = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20,
        choices=[
            ("online", "Online Payment"),
            ("cod", "Cash on Delivery"),
        ],blank=True,default="")

    payment_status = models.CharField(max_length=20,
        choices=[
            ("pending", "Pending"),
            ("paid", "Paid"),
            ("failed", "Failed"),
        ],default="pending")

    # Delivery tracking statuses
    TRACKING_STATUS_CHOICES = [
        ('created', 'Created'),
        ('placed', 'Order Placed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    tracking_status = models.CharField(max_length=30,choices=TRACKING_STATUS_CHOICES,default='created')

    # Delivery stage timestamps
    placed_at = models.DateTimeField(null=True, blank=True, editable=False)
    processing_at = models.DateTimeField(null=True, blank=True, editable=False)
    shipped_at = models.DateTimeField(null=True, blank=True, editable=False)
    out_for_delivery_at = models.DateTimeField(null=True, blank=True, editable=False)
    delivered_at = models.DateTimeField(null=True, blank=True, editable=False)
    tracking_updated_at = models.DateTimeField(null=True, blank=True)

    # Return tracking statuses
    RETURN_STATUS_CHOICES = [
        ('not_requested', 'No Return Requested'),
        ('requested', 'Return Requested'),
        ('approved', 'Return Approved'),
        ('pickup_scheduled', 'Pickup Scheduled'),
        ('picked_up', 'Item Picked Up'),
        ('received', 'Item Received'),
        ('refund_processing', 'Refund Processing'),
        ('refunded', 'Refunded'),
        ('rejected', 'Return Rejected'),
        ('cancelled', 'Return Cancelled'),
    ]

    return_status = models.CharField(max_length=30,choices=RETURN_STATUS_CHOICES,default='not_requested')

    # Return stage timestamps
    return_requested_at = models.DateTimeField(null=True, blank=True, editable=False)
    return_approved_at = models.DateTimeField(null=True, blank=True, editable=False)
    pickup_scheduled_at = models.DateTimeField(null=True, blank=True, editable=False)
    return_picked_up_at = models.DateTimeField(null=True, blank=True, editable=False)
    return_received_at = models.DateTimeField(null=True, blank=True, editable=False)
    refund_processing_at = models.DateTimeField(null=True, blank=True, editable=False)
    refunded_at = models.DateTimeField(null=True, blank=True, editable=False)
    return_rejected_at = models.DateTimeField(null=True, blank=True, editable=False)
    return_cancelled_at = models.DateTimeField(null=True, blank=True, editable=False)
    return_updated_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        delivery_timestamps = {
            'placed': 'placed_at',
            'processing': 'processing_at',
            'shipped': 'shipped_at',
            'out_for_delivery': 'out_for_delivery_at',
            'delivered': 'delivered_at',
        }

        return_timestamps = {
            'requested': 'return_requested_at',
            'approved': 'return_approved_at',
            'pickup_scheduled': 'pickup_scheduled_at',
            'picked_up': 'return_picked_up_at',
            'received': 'return_received_at',
            'refund_processing': 'refund_processing_at',
            'refunded': 'refunded_at',
            'rejected': 'return_rejected_at',
            'cancelled': 'return_cancelled_at',
        }
        now = timezone.now()
        old = None
        if self.pk:
            old = type(self).objects.filter(pk=self.pk).values(
                'tracking_status',
                'return_status'
            ).first()

        if old is None or old['tracking_status'] != self.tracking_status:
            timestamp_field = delivery_timestamps.get(self.tracking_status)

            if timestamp_field and not getattr(self, timestamp_field):
                setattr(self, timestamp_field, now)

            self.tracking_updated_at = now

        if old is None or old['return_status'] != self.return_status:
            timestamp_field = return_timestamps.get(self.return_status)

            if timestamp_field and not getattr(self, timestamp_field):
                setattr(self, timestamp_field, now)

            if self.return_status != 'not_requested':
                self.return_updated_at = now

        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_id

class OrderItem(models.Model):

    RETURN_STATUS_CHOICES = [
        ('not_requested', 'Not Requested'),
        ('requested', 'Return Requested'),
        ('approved', 'Return Approved'),
        ('pickup_scheduled', 'Pickup Scheduled'),
        ('picked_up', 'Item Picked Up'),
        ('received', 'Item Received'),
        ('refund_processing', 'Refund Processing'),
        ('refunded', 'Refunded'),
        ('rejected', 'Return Rejected'),
        ('cancelled', 'Return Cancelled'),
    ]

    order = models.ForeignKey(Order,related_name='items',on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    unitprice = models.DecimalField(decimal_places=2,max_digits=11,default=0)
    amount = models.DecimalField(decimal_places=2,max_digits=11,default=0)
    quantity = models.IntegerField()
    variant = models.ForeignKey(ProductVariant,on_delete=models.SET_NULL,null=True,
    blank=True,related_name="order_items_variants")
    return_eligible = models.BooleanField(default=True)
    return_status = models.CharField(max_length=30,choices=RETURN_STATUS_CHOICES,default='not_requested')
    return_reason = models.TextField(blank=True, null=True)
    return_requested_at = models.DateTimeField(null=True, blank=True)
    return_approved_at = models.DateTimeField(null=True, blank=True)
    pickup_scheduled_at = models.DateTimeField(null=True, blank=True)
    return_picked_up_at = models.DateTimeField(null=True, blank=True)
    return_received_at = models.DateTimeField(null=True, blank=True)
    refund_processing_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    return_rejected_at = models.DateTimeField(null=True, blank=True)
    return_cancelled_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f'{self.quantity} of {self.product.name}'

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant,on_delete=models.SET_NULL,null=True,blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    related_order = models.CharField(max_length=36, blank=True, default="")

    class Meta:
        unique_together = ("user", "product", "variant")

    def save(self, *args, **kwargs):
        self.amount = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.quantity}x {self.product.name} "
            f"for {self.user.username}"
        )

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    address = models.TextField()
    profile_picture = models.ImageField(upload_to="profile_pictures/",blank=True,null=True,)

    def __str__(self):
        return self.user.username


