
from django.contrib import admin, messages
from django.utils import timezone

from .models import (
    Product,
    ProductVariant,
    Order,
    OrderItem,
    CartItem,
    UserProfile,
)


# ==================================================
# ROLE-BASED ADMIN SECURITY
# ==================================================

class RoleBasedAdminMixin:

    ROLE_NAMES = (
        "Product Manager",
        "Order Manager",
        "Support Staff",
    )

    # Configure access separately for each admin class.
    VIEW_ROLES = ()
    ADD_ROLES = ()
    CHANGE_ROLES = ()
    DELETE_ROLES = ()

    ROLE_FIELDS = {}
    ROLE_READONLY_FIELDS = {}

    ROLE_LIST_DISPLAY = {}
    ROLE_LIST_FILTER = {}
    ROLE_SEARCH_FIELDS = {}

    def get_user_role(self, request):
        if request.user.is_superuser:
            return "Super Admin"

        user_groups = set(
            request.user.groups.values_list("name", flat=True)
        )

        matching_roles = user_groups.intersection(self.ROLE_NAMES)

        # Avoid ambiguous access if a user belongs to multiple roles.
        if len(matching_roles) != 1:
            return None

        return matching_roles.pop()

    def has_module_permission(self, request):
        role = self.get_user_role(request)

        return (
            role == "Super Admin"
            or role in self.VIEW_ROLES
            or role in self.ADD_ROLES
            or role in self.CHANGE_ROLES
        )

    def has_view_permission(self, request, obj=None):
        role = self.get_user_role(request)

        return (
            role == "Super Admin"
            or role in self.VIEW_ROLES
        )

    def has_add_permission(self, request):
        role = self.get_user_role(request)

        return (
            role == "Super Admin"
            or role in self.ADD_ROLES
        )

    def has_change_permission(self, request, obj=None):
        role = self.get_user_role(request)

        return (
            role == "Super Admin"
            or role in self.CHANGE_ROLES
        )

    def has_delete_permission(self, request, obj=None):
        role = self.get_user_role(request)

        return (
            role == "Super Admin"
            or role in self.DELETE_ROLES
        )

    def get_fields(self, request, obj=None):
        role = self.get_user_role(request)

        if role == "Super Admin":
            return super().get_fields(request, obj)

        fields = super().get_fields(request, obj)
        allowed_fields = self.ROLE_FIELDS.get(role)

        # None means all model fields are allowed for this role.
        if allowed_fields is None:
            return fields

        allowed_fields = set(allowed_fields)

        return [
            field for field in fields
            if field in allowed_fields
        ]

    def get_readonly_fields(self, request, obj=None):
        role = self.get_user_role(request)

        if role == "Super Admin":
            return super().get_readonly_fields(request, obj)

        readonly = set(
            super().get_readonly_fields(request, obj)
        )

        readonly.update(
            self.ROLE_READONLY_FIELDS.get(role, ())
        )

        return tuple(readonly)

    def get_list_display(self, request):
        role = self.get_user_role(request)

        if role == "Super Admin":
            return super().get_list_display(request)

        return self.ROLE_LIST_DISPLAY.get(
            role,
            super().get_list_display(request)
        )

    def get_list_filter(self, request):
        role = self.get_user_role(request)

        if role == "Super Admin":
            return super().get_list_filter(request)

        return self.ROLE_LIST_FILTER.get(role, ())

    def get_search_fields(self, request):
        role = self.get_user_role(request)

        if role == "Super Admin":
            return super().get_search_fields(request)

        return self.ROLE_SEARCH_FIELDS.get(role, ())


# ==================================================
# USER PROFILE
# ==================================================

@admin.register(UserProfile)
class UserProfileAdmin(RoleBasedAdminMixin, admin.ModelAdmin):

    VIEW_ROLES = (
        "Order Manager",
        "Support Staff",
    )

    # Profiles are view-only for these roles.
    ROLE_FIELDS = {
        "Order Manager": None,
        "Support Staff": None,
    }

    def get_readonly_fields(self, request, obj=None):
        if self.get_user_role(request) == "Super Admin":
            return super().get_readonly_fields(request, obj)

        return tuple(field.name for field in self.model._meta.fields)


# ==================================================
# PRODUCT
# ==================================================

@admin.register(Product)
class ProductAdmin(RoleBasedAdminMixin, admin.ModelAdmin):

    VIEW_ROLES = (
        "Product Manager",
        "Order Manager",
        "Support Staff",
    )

    ADD_ROLES = ("Product Manager",)
    CHANGE_ROLES = ("Product Manager",)

    ROLE_FIELDS = {
        "Product Manager": None,

        "Order Manager": [
            "product_code",
            "name",
            "category",
            "price",
            "stock",
        ],

        "Support Staff": [
            "product_code",
            "name",
            "category",
        ],
    }

    ROLE_READONLY_FIELDS = {
        "Order Manager": [
            "product_code",
            "name",
            "category",
            "price",
            "stock",
        ],

        "Support Staff": [
            "product_code",
            "name",
            "category",
        ],
    }

    list_display = [
        "product_code",
        "name",
        "description",
        "price",
        "stock",
        "created_date",
        "image",
        "is_returnable",
    ]

    list_filter = [
        "is_returnable",
        "created_date",
    ]

    search_fields = [
        "product_code",
        "name",
    ]

    ROLE_LIST_DISPLAY = {
        "Order Manager": [
            "product_code",
            "name",
            "category",
            "price",
            "stock",
        ],

        "Support Staff": [
            "product_code",
            "name",
            "category",
        ],
    }


# ==================================================
# PRODUCT VARIANT
# ==================================================

@admin.register(ProductVariant)
class ProductVariantAdmin(RoleBasedAdminMixin, admin.ModelAdmin):

    VIEW_ROLES = (
        "Product Manager",
        "Order Manager",
        "Support Staff",
    )

    ADD_ROLES = ("Product Manager",)
    CHANGE_ROLES = ("Product Manager",)

    ROLE_FIELDS = {
        "Product Manager": None,
        "Order Manager": None,
        "Support Staff": None,
    }

    ROLE_READONLY_FIELDS = {
        "Order Manager": tuple(
            field.name for field in ProductVariant._meta.fields
        ),
        "Support Staff": tuple(
            field.name for field in ProductVariant._meta.fields
        ),
    }


# ==================================================
# ORDER
# ==================================================

@admin.register(Order)
class OrderAdmin(RoleBasedAdminMixin, admin.ModelAdmin):

    VIEW_ROLES = (
        "Product Manager",
        "Order Manager",
        "Support Staff",
    )

    CHANGE_ROLES = ("Order Manager","Support Staff",)

    list_display = [
        "order_id",
        "user",
        "amount",
        "status",
        "tracking_status",
        "return_status",
        "payment_status",
        "created_date",
        "updated_date",
    ]

    list_filter = (
        "status",
        "tracking_status",
        "return_status",
        "payment_status",
    )

    search_fields = (
        "order_id",
        "user__username",
        "user__email",
    )

    readonly_fields = (
        "placed_at",
        "processing_at",
        "shipped_at",
        "out_for_delivery_at",
        "delivered_at",
        "tracking_updated_at",
        "return_requested_at",
        "return_approved_at",
        "pickup_scheduled_at",
        "return_picked_up_at",
        "return_received_at",
        "refund_processing_at",
        "refunded_at",
        "return_rejected_at",
        "return_cancelled_at",
        "return_updated_at",
    )

    ORDER_FIELDS = [
        "order_id",
        "user",
        "amount",
        "status",
        "delivery_address",
        "payment_method",
        "payment_status",
        "tracking_status",
        "return_status",
        "placed_at",
        "processing_at",
        "shipped_at",
        "out_for_delivery_at",
        "delivered_at",
        "tracking_updated_at",
        "created_date",
        "updated_date",
    ]

    ROLE_FIELDS = {
        "Order Manager": ORDER_FIELDS,

        "Support Staff": [
            "order_id",
            "user",
            "status",
            "created_date",
            "delivery_address",
            "tracking_status",
        ],

        "Product Manager": [
            "order_id",
            "status",
            "created_date",
        ],
    }

    ROLE_READONLY_FIELDS = {
        "Order Manager": [
            "order_id",
            "user",
            "amount",
            "payment_method",
            "payment_status",
            "delivery_address",
            "created_date",
            "updated_date",
        ],

        "Support Staff": [
            "order_id",
            "user",
            "amount",
            "tracking_status",
            "payment_method",
            "payment_status",
            "delivery_address",
            "created_date",
            "updated_date",
            "return_status",
            "return_requested_at",
            "return_approved_at",
            "pickup_scheduled_at",
            "return_picked_up_at",
            "return_received_at",
            "refund_processing_at",
            "refunded_at",
            "return_rejected_at",
            "return_cancelled_at",
            "return_updated_at",
        ],

        "Product Manager": [
            "order_id",
            "status",
            "created_date",
        ],
    }

    ROLE_LIST_DISPLAY = {
        "Order Manager": [
            "order_id",
            "user",
            "amount",
            "status",
            "tracking_status",
            "return_status",
            "payment_status",
            "created_date",
        ],

        "Support Staff": [
            "order_id",
            "user",
            "status",
            "tracking_status",
            "created_date",
        ],

        "Product Manager": [
            "order_id",
            "status",
            "created_date",
        ],
    }

    ROLE_LIST_FILTER = {
    "Order Manager": (
        "status",
        "tracking_status",
        "return_status",
        "payment_status",
    ),

    "Support Staff": (
        "status",
        "tracking_status",
    ),

    "Product Manager": (
        "status",
    ),
    }


    ROLE_SEARCH_FIELDS = {
        "Order Manager": (
            "order_id",
            "user__username",
            "user__email",
        ),

        "Support Staff": (
            "order_id",
            "user__username",
            "user__email",
        ),

        "Product Manager": (
            "order_id",
        ),
    }


# ==================================================
# ORDER ITEM RETURN ACTIONS
# ==================================================

def is_order_manager(request):
    if request.user.is_superuser:
        return True

    role_groups = request.user.groups.filter(
        name__in=[
            "Product Manager",
            "Order Manager",
            "Support Staff",
        ]
    )

    return (
        role_groups.count() == 1
        and role_groups.filter(name="Order Manager").exists()
    )


@admin.action(description="Approve selected return requests")
def approve_returns(modeladmin, request, queryset):

    if not is_order_manager(request):
        messages.error(request, "You are not authorized.")
        return

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

    if not is_order_manager(request):
        messages.error(request, "You are not authorized.")
        return

    eligible = queryset.filter(return_status="requested")

    count = eligible.update(
        return_status="rejected",
        return_rejected_at=timezone.now(),
    )

    messages.success(
        request,
        f"{count} return request(s) rejected."
    )


@admin.action(description="Mark as pickup scheduled")
def mark_pickup_scheduled(modeladmin, request, queryset):

    if not is_order_manager(request):
        messages.error(request, "You are not authorized.")
        return

    count = queryset.filter(
        return_status="approved"
    ).update(
        return_status="pickup_scheduled",
        pickup_scheduled_at=timezone.now(),
    )

    messages.success(request, f"{count} item(s) updated.")


@admin.action(description="Mark as picked up")
def mark_picked_up(modeladmin, request, queryset):

    if not is_order_manager(request):
        messages.error(request, "You are not authorized.")
        return

    count = queryset.filter(
        return_status="pickup_scheduled"
    ).update(
        return_status="picked_up",
        return_picked_up_at=timezone.now(),
    )

    messages.success(request, f"{count} item(s) updated.")


@admin.action(description="Mark as received")
def mark_received(modeladmin, request, queryset):

    if not is_order_manager(request):
        messages.error(request, "You are not authorized.")
        return

    count = queryset.filter(
        return_status="picked_up"
    ).update(
        return_status="received",
        return_received_at=timezone.now(),
    )

    messages.success(request, f"{count} item(s) updated.")


@admin.action(description="Start refund processing")
def start_refund(modeladmin, request, queryset):

    if not is_order_manager(request):
        messages.error(request, "You are not authorized.")
        return

    count = queryset.filter(
        return_status="received"
    ).update(
        return_status="refund_processing",
        refund_processing_at=timezone.now(),
    )

    messages.success(request, f"{count} refund(s) processing.")


@admin.action(description="Mark refund as completed")
def complete_refund(modeladmin, request, queryset):

    if not is_order_manager(request):
        messages.error(request, "You are not authorized.")
        return

    count = queryset.filter(
        return_status="refund_processing"
    ).update(
        return_status="refunded",
        refunded_at=timezone.now(),
    )

    messages.success(request, f"{count} refund(s) completed.")


# ==================================================
# ORDER ITEM
# ==================================================

@admin.register(OrderItem)
class OrderItemAdmin(RoleBasedAdminMixin, admin.ModelAdmin):

    VIEW_ROLES = (
        "Product Manager",
        "Order Manager",
        "Support Staff",
    )

    CHANGE_ROLES = ("Order Manager","Support Staff")

    list_display = [
        "id",
        "order",
        "product",
        "quantity",
        "unitprice",
        "amount",
        "return_eligible",
        "return_status",
        "return_requested_at",
        "refunded_at",
    ]

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

    ROLE_FIELDS = {
        "Order Manager": None,

        "Support Staff": [
            "id",
            "order",
            "product",
            "quantity",
            "unitprice",
            "amount",
            "return_eligible",
            "return_status",
            "return_requested_at",
        ],

        "Product Manager": [
            "id",
            "order",
            "product",
            "quantity",
            "unitprice",
            "amount",
        ],
    }

    ROLE_READONLY_FIELDS = {
        "Support Staff": [
            "id",
            "order",
            "product",
            "quantity",
            "unitprice",
            "amount",
            "return_eligible",
            # "return_status",
            "return_requested_at",
        ],

        "Product Manager": [
            "id",
            "order",
            "product",
            "quantity",
            "unitprice",
            "amount",
        ],
    }

    ROLE_LIST_FILTER = {
    "Order Manager": (
        "return_status",
        "return_eligible",
        "return_requested_at",
        "refunded_at",
    ),

    "Support Staff": (
        "return_status",
        "return_eligible",
        "return_requested_at",
        "refunded_at",
    ),

    "Product Manager": (
        "return_eligible",
    ),
    }

    ROLE_SEARCH_FIELDS = {
        "Order Manager": (
            "order_id",
            "user__username",
            "user__email",
        ),

        "Support Staff": (
            "order_id",
            "user__username",
            "user__email",
        ),

        "Product Manager": (
            "order_id",
        ),
    }

    actions = [
        approve_returns,
        reject_returns,
        mark_pickup_scheduled,
        mark_picked_up,
        mark_received,
        start_refund,
        complete_refund,
    ]

    def get_actions(self, request):
        if self.get_user_role(request) != "Order Manager" and not request.user.is_superuser:
            return {}

        return super().get_actions(request)

    list_per_page = 25


# ==================================================
# CART ITEM
# ==================================================

@admin.register(CartItem)
class CartItemAdmin(RoleBasedAdminMixin, admin.ModelAdmin):

    VIEW_ROLES = (
        "Product Manager",
        "Order Manager",
        "Support Staff",
    )

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

    ROLE_FIELDS = {
        "Product Manager": None,
        "Order Manager": None,
        "Support Staff": None,
    }

    ROLE_READONLY_FIELDS = {
        "Product Manager": tuple(
            field.name for field in CartItem._meta.fields
        ),
        "Order Manager": tuple(
            field.name for field in CartItem._meta.fields
        ),
        "Support Staff": tuple(
            field.name for field in CartItem._meta.fields
        ),
    }


# ==================================================
# ADMIN HEADER
# ==================================================

admin.site.site_header = "Administrator"
admin.site.site_title = "Ecommerce Administration"
admin.site.index_title = "Store Management"
