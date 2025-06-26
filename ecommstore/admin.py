from django.contrib import admin
from .models import Product, ProductVariant, Order, OrderItem, CartItem, UserProfile

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(ProductVariant)

class ProductAdmin(admin.ModelAdmin):
    list_display = ["product_code","name","description","price","stock","created_date","image"]

admin.site.register(Product,ProductAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_id","user","amount","status","created_date","updated_date"]

admin.site.register(Order,OrderAdmin)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order","product","unitprice","amount","quantity"]

admin.site.register(OrderItem,OrderItemAdmin)

class CartItemAdmin(admin.ModelAdmin):
    list_display = ["id","user","product","variant","quantity","added_at","updated_at"]

admin.site.register(CartItem,CartItemAdmin)

admin.site_header = "Administrator"