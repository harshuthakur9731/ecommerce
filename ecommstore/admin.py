from django.contrib import admin
from .models import Product, ProductVariant, Order, OrderItem, CartItem, Customer

# Register your models here.
admin.site.register(OrderItem)
admin.site.register(Customer)
admin.site.register(ProductVariant)
admin.site.register(CartItem)


class ProductAdmin(admin.ModelAdmin):
    list_display = ["product_code","name","description","price","stock","created_date","image"]

admin.site.register(Product,ProductAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_id","user","created_date","updated_date"]

admin.site.register(Order,OrderAdmin)

admin.site_header = "Administrator"