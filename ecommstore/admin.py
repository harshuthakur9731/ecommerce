from django.contrib import admin
from .models import Product, ProductVariant, Order, OrderItem, CartItem, Customer

# Register your models here.
admin.site.register(OrderItem)
admin.site.register(Customer)
admin.site.register(ProductVariant)

class ProductAdmin(admin.ModelAdmin):
    list_display = ["product_code","name","description","price","stock","created_date","image"]

admin.site.register(Product,ProductAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_id","user","created_date","updated_date"]

admin.site.register(Order,OrderAdmin)

class CartItemAdmin(admin.ModelAdmin):
    list_display = ["user","product","variant","quantity","added_at","updated_at"]

admin.site.register(CartItem,CartItemAdmin)

admin.site_header = "Administrator"