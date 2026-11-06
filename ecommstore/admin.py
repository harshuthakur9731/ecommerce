from django.contrib import admin
from .models import Product, ProductVariant, Order, OrderItem, CartItem, UserProfile

# Register your models here.

# ----------------------------------
# User Profile
# ----------------------------------
admin.site.register(UserProfile)

# ----------------------------------
# Product Variant
# ----------------------------------
admin.site.register(ProductVariant)

# ----------------------------------
# Product
# ----------------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["product_code","name","description","price","stock","created_date","image","is_returnable"]
    list_filter = ["is_returnable","created_date",]
    search_fields = ["product_code","name",]

# ----------------------------------
# Order Actions
# ----------------------------------

@admin.action(description="Approve selected return requests")
def approve_returns(modeladmin, request, queryset):

    eligible = queryset.filter(return_status="requested")

    count = eligible.update(
        return_status="approved",
        return_approved_at=timezone.now(),
    )

    messages.success(
        request,
        f"{count} return request(s) approved."
    )


@admin.action(description="Reject selected return requests")
def reject_returns(modeladmin, request, queryset):

    eligible = queryset.filter(return_status="requested")

    count = eligible.update(
        return_status="rejected",
        return_rejected_at=timezone.now(),
    )

    messages.success(
        request,
        f"{count} return request(s) rejected."
    )


# ----------------------------------
# Return Progress Actions
# ----------------------------------

@admin.action(description="Mark as pickup scheduled")
def mark_pickup_scheduled(modeladmin, request, queryset):

    count = queryset.filter(
        return_status="approved"
    ).update(
        return_status="pickup_scheduled",
        pickup_scheduled_at=timezone.now(),
    )

    messages.success(request, f"{count} item(s) updated.")


@admin.action(description="Mark as picked up")
def mark_picked_up(modeladmin, request, queryset):

    count = queryset.filter(
        return_status="pickup_scheduled"
    ).update(
        return_status="picked_up",
        return_picked_up_at=timezone.now(),
    )

    messages.success(request, f"{count} item(s) updated.")


@admin.action(description="Mark as received")
def mark_received(modeladmin, request, queryset):

    count = queryset.filter(
        return_status="picked_up"
    ).update(
        return_status="received",
        return_received_at=timezone.now(),
    )

    messages.success(request, f"{count} item(s) updated.")


# ----------------------------------
# Refund Actions
# ----------------------------------

@admin.action(description="Start refund processing")
def start_refund(modeladmin, request, queryset):

    count = queryset.filter(
        return_status="received"
    ).update(
        return_status="refund_processing",
        refund_processing_at=timezone.now(),
    )

    messages.success(request, f"{count} refund(s) processing.")


@admin.action(description="Mark refund as completed")
def complete_refund(modeladmin, request, queryset):

    count = queryset.filter(
        return_status="refund_processing"
    ).update(
        return_status="refunded",
        refunded_at=timezone.now(),
    )

    messages.success(request, f"{count} refund(s) completed.")

# ----------------------------------
# Order
# ----------------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = ["order_id","user","amount","status",'tracking_status','return_status',
    'payment_status',"created_date","updated_date"]

    list_filter = ('status','tracking_status','return_status','payment_status',)

    search_fields = ("order_id","user__username","user__email",)

    readonly_fields = ('placed_at','processing_at','shipped_at','out_for_delivery_at','delivered_at',
    'tracking_updated_at','return_requested_at','return_approved_at','pickup_scheduled_at','return_picked_up_at',
    'return_received_at','refund_processing_at','refunded_at','return_rejected_at','return_cancelled_at',
    'return_updated_at',
    )

# ----------------------------------
# Order Item - Individual Returns
# ----------------------------------

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["id","order","product","quantity","unitprice","amount","return_eligible",
    "return_status","return_requested_at","refunded_at",]

    list_filter = (
        "return_status",
        "return_eligible",
        "return_requested_at",
        "refunded_at",
    )

    search_fields = (
        "order__order_id",
        "product__name",
        "order__user__username",
        "order__user__email",
    )

    readonly_fields = (
        "return_requested_at",
        "return_approved_at",
        "pickup_scheduled_at",
        "return_picked_up_at",
        "return_received_at",
        "refund_processing_at",
        "refunded_at",
        "return_rejected_at",
        "return_cancelled_at",
    )

    actions = [
        approve_returns,
        reject_returns,
        mark_pickup_scheduled,
        mark_picked_up,
        mark_received,
        start_refund,
        complete_refund,
    ]

    list_per_page = 25

# ----------------------------------
# Cart Item
# ----------------------------------

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "product",
        "variant",
        "quantity",
        "added_at",
        "updated_at",
    ]

    search_fields = [
        "user__username",
        "product__name",
    ]

# ----------------------------------
# Admin Header
# ----------------------------------

admin.site.site_header = "Administrator"
admin.site.site_title = "Ecommerce Administration"
admin.site.index_title = "Store Management"
