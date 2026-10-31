from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from .models import Product,CartItem,UserProfile,Order,OrderItem,ProductVariant
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
import logging
import uuid
from django.urls import reverse
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpResponseNotAllowed
from django.views.decorators.http import require_POST
User = get_user_model()
logger = logging.getLogger(__name__)

# # logger.info("Order retrieved: %s", order.pk)
# logger.debug("Cart contains %s items", len(cart_items))

# Create your views here.
@login_required
def home(request):
    products = Product.objects.all()
    userprofile = UserProfile.objects.filter(user=request.user)
    profilepicture = ''
    if len(userprofile) > 0:
        profilepicture = userprofile[0].profile_picture
    images = [
        '/static/fashion25.png',
        '/static/fashiongirl.png',       
        '/static/fashion10.png',
    ]
    return render(request,'ecommstore/templates/base.html',{'products': products,'images': images,'profilepicture':profilepicture})

@require_POST
def signup(request):
    username = request.POST.get("name", "").strip()
    email = request.POST.get("email", "").strip()
    password = request.POST.get("pswd", "")

    if not username or not email or not password:
        messages.error(
            request,
            "Username, email, and password are required.",
        )
        return redirect("login")

    if User.objects.filter(username=username).exists():
        messages.error(request, "Username already exists.")
        return redirect("login")

    User.objects.create_user(
        username=username,
        email=email,
        password=password,
    )

    messages.success(
        request,
        "Your account has been created successfully!",
    )
    return redirect("login")

def shop(request):
    userprofile = UserProfile.objects.filter(user=request.user)
    profilepicture = ''
    if len(userprofile) > 0:
        profilepicture = userprofile[0].profile_picture
    images = [
        '/static/fashion25.png',
        '/static/fashiongirl.png',       
        '/static/fashion10.png',
    ]
    return render(request,'ecommstore/templates/shop.html',{'profilepicture':profilepicture})



@login_required
def account(request):
    userprofile = UserProfile.objects.filter(
        user=request.user
    ).first()

    profilepicture = (
        userprofile.profile_picture
        if userprofile and userprofile.profile_picture
        else ""
    )
    address = userprofile.address if userprofile else ""

    myOrders = Order.objects.filter(
        user=request.user
    ).order_by("-created_date")[:10]

    return render(
        request,
        "ecommstore/templates/account.html",
        {
            "profilepicture": profilepicture,
            "address": address,
            "myOrders": myOrders,
        },
    )

def logout(request):
    return render(request,'ecommstore/templates/base.html')

def login(request):
    return render(request,'ecommstore/templates/base.html')

#def signup(request):
    return render(request,'ecommstore/templates/base.html')


def itemdetail(request, PCode):
    product = get_object_or_404(
        Product,
        product_code=PCode,
    )

    profile = None
    if request.user.is_authenticated:
        profile = UserProfile.objects.filter(
            user=request.user
        ).first()

    variants = ProductVariant.objects.filter(
            product=product
        ).order_by("variant_name")

    return render(
        request,
        "ecommstore/templates/itemdetail.html",
        {
            "product": product,
            "product_code": product.product_code,
            "name": product.name,
            "image": product.image,
            "description": product.description,
            "price": product.price,
            "instock": product.stock,
            "specifications": product.specification,
            "termsnconditions": product.termsnconditions,
            "desc1": product.desc1,
            "image1": product.image1,
            "image2": product.image2,
            "image3": product.image3,
            "images": [
                product.image,
                product.image1,
                product.image2,
                product.image3,
            ],
            "profilepicture": (
                profile.profile_picture if profile else ""
            ),
            "variants": variants,
            "has_variants": variants.exists(),
        },
    )


@login_required
def cart(request):
    cart_items = list(
        CartItem.objects
        .filter(user=request.user)
        .select_related("product", "variant")
        .order_by("id")
    )

    total_amount = Decimal("0.00")

    for item in cart_items:
        item.amount = item.quantity * item.price
        total_amount += item.amount

    profile = UserProfile.objects.filter(
        user=request.user
    ).first()

    return render(
        request,
        "ecommstore/templates/cartdetail.html",
        {
            "cart_items": cart_items,
            "total_amount": total_amount,
            "profilepicture": (
                profile.profile_picture if profile else ""
            ),
            "cart_count": sum(item.quantity for item in cart_items),
        },
    )

@login_required
@require_POST
def resetcart(request):
    CartItem.objects.filter(user=request.user).delete()

    messages.success(request, "Your cart has been cleared.")
    return redirect("cart")



@require_POST
@login_required
def addToCartAct(request, PCode):
    variant_id = request.POST.get("variant_id")

    with transaction.atomic():
        product = get_object_or_404(
            Product.objects.select_for_update(),
            product_code=PCode
        )

        has_variants = ProductVariant.objects.filter(
            product=product
        ).exists()

        variant = None

        if has_variants:
            if not variant_id:
                messages.error(request, "Please select a product variant.")
                return redirect("itemdetail", PCode=PCode)

            variant = get_object_or_404(
                ProductVariant.objects.select_for_update(),
                id=variant_id,
                product=product
            )
            available_stock = variant.stock

        else:
            if variant_id:
                messages.error(request, "Invalid product variant.")
                return redirect("itemdetail", PCode=PCode)

            available_stock = product.stock

        item = CartItem.objects.filter(
            user=request.user,
            product=product,
            variant=variant,
            related_order=""
        ).first()

        current_quantity = item.quantity if item else 0

        if current_quantity + 1 > available_stock:
            messages.warning(
                request,
                f"Only {available_stock} units are available."
            )
            return redirect("itemdetail", PCode=PCode)

        if item:
            item.quantity += 1
            item.price = product.price
            item.save()
        else:
            CartItem.objects.create(
                user=request.user,
                product=product,
                variant=variant,
                quantity=1,
                price=product.price,
                related_order=""
            )

    messages.success(request, "Product added to your cart.")
    return redirect("cart")


@login_required
@require_POST
def delToCartAct(request, itemid):
    item = get_object_or_404(
        CartItem,
        id=itemid,
        user=request.user,
    )
    item.delete()

    messages.success(request, "Item removed from your cart.")
    return redirect("cart")

def get_cart_context(user):
    cart_items = list(
        CartItem.objects
        .filter(user=user)
        .select_related("product", "variant")
        .order_by("id")
    )

    total_amount = Decimal("0.00")

    for item in cart_items:
        item.amount = item.quantity * item.price
        total_amount += item.amount

    profile = UserProfile.objects.filter(user=user).first()

    return {
        "cart_items": cart_items,
        "total_amount": total_amount,
        "profilepicture": (
            profile.profile_picture if profile else ""
        ),
        "cart_count": sum(item.quantity for item in cart_items),
    }

@login_required
@require_POST
def updateCartQuantity(request, itemid):
    action = request.POST.get("action")

    with transaction.atomic():
        item = get_object_or_404(
            CartItem.objects.select_for_update().select_related(
                "product", "variant"
            ),
            id=itemid,
            user=request.user,
            related_order=""
        )

        if item.variant_id:
            variant = ProductVariant.objects.select_for_update().get(
                id=item.variant_id
            )
            available_stock = variant.stock
        else:
            product = Product.objects.select_for_update().get(
                product_code=item.product_id
            )
            available_stock = product.stock

        if action == "increase":
            if item.quantity < available_stock:
                item.quantity += 1
                item.save()
                messages.success(request, "Quantity updated.")
            else:
                messages.warning(
                    request,
                    "You have reached the available stock limit."
                )

        elif action == "decrease":
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
                messages.success(request, "Quantity updated.")
            else:
                messages.info(
                    request,
                    "Minimum quantity is 1. Remove the item instead."
                )
        else:
            messages.error(request, "Invalid quantity action.")

    return redirect("cart")

@login_required
@require_POST
def order(request):
    with transaction.atomic():

        cart_items = list(
            CartItem.objects.select_for_update()
            .filter(user=request.user, related_order="")
            .select_related("product", "variant")
            .order_by("id")
        )

        if not cart_items:
            messages.warning(request, "Your cart is empty.")
            return redirect("cart")

        # Get user's default delivery address
        profile = UserProfile.objects.filter(user=request.user).first()

        delivery_address = (
            profile.address
            if profile and profile.address
            else ""
        )

        # Generate order ID
        order_id = f"ODR-{uuid.uuid4().hex.upper()}"

        # Create order
        new_order = Order.objects.create(
            order_id=order_id,
            user=request.user,
            status="created",
            delivery_address=delivery_address
        )

        order_lines = []
        order_subtotal = Decimal("0.00")

        # Create order items
        for item in cart_items:

            item_amount = item.price * item.quantity

            order_lines.append(
                OrderItem(
                    order=new_order,
                    product=item.product,
                    variant=item.variant,
                    quantity=item.quantity,
                    unitprice=item.price,
                    amount=item_amount
                )
            )

            order_subtotal += item_amount

        OrderItem.objects.bulk_create(order_lines)

        # Calculate shipping charges
        if order_subtotal > Decimal("699.00"):
            shipping_charge = Decimal("0.00")
        else:
            shipping_charge = Decimal("50.00")

        # Calculate final payable amount
        grand_total = order_subtotal + shipping_charge

        # Save order price details
        new_order.subtotal = order_subtotal
        new_order.shipping_charge = shipping_charge
        new_order.amount = grand_total

        new_order.save(
            update_fields=[
                "subtotal",
                "shipping_charge",
                "amount"
            ]
        )

        # Associate cart items with this order
        CartItem.objects.filter(
            user=request.user,
            id__in=[item.id for item in cart_items]
        ).update(related_order=order_id)

    # Retrieve order items
    order_items = (
        OrderItem.objects.filter(order=new_order)
        .select_related("product", "variant")
        .order_by("id")
    )

    CartItem.objects.filter(
            user=request.user,
            related_order=order_id
        ).delete()

    return render(
        request,
        "ecommstore/templates/ordersummary.html",
        {
            "order_items": enumerate(order_items),
            "orderamount": order_subtotal,
            "shippingcharge": shipping_charge,
            "grandtotal": grand_total,
            "order": new_order.order_id,
            "order_object": new_order,
        }
    )

@login_required
@require_POST
def confirmorder(request, orderid):

    payment_method = request.POST.get("payment_method")

    with transaction.atomic():

        order_obj = get_object_or_404(
            Order.objects.select_for_update(),
            order_id=orderid,
            user=request.user
        )

        if order_obj.status != "created":
            messages.warning(
                request,
                "This order has already been processed or cannot be confirmed."
            )
            return redirect("vieworder", orderid=orderid)

        # Validate payment method
        if payment_method not in ("online", "cod"):
            messages.error(request, "Please select a valid payment method.")
            return redirect("vieworder", orderid=orderid)

        # COD eligibility: subtotal must be <= ₹699
        if (
            payment_method == "cod"
            and order_obj.subtotal > Decimal("699.00")
        ):
            messages.error(
                request,
                "Cash on Delivery is not available for orders above ₹699. "
                "Please choose online payment."
            )
            return redirect("vieworder", orderid=orderid)

        # Online payment must go through a payment gateway.
        # Do not place the order or deduct stock before payment verification.
        if payment_method == "online":
            messages.info(
                request,
                "Please continue to online payment to complete your order."
            )
            return redirect("vieworder", orderid=orderid)

        order_items = list(
            OrderItem.objects.filter(order=order_obj)
            .select_related("product", "variant")
            .order_by("id")
        )

        if not order_items:
            messages.error(request, "This order has no items.")
            return redirect("cart")

        # First validate all stock. Do not deduct anything yet.
        stock_records = []

        for order_item in order_items:

            if order_item.variant_id:

                variant = ProductVariant.objects.select_for_update().filter(
                    id=order_item.variant_id,
                    product=order_item.product
                ).first()

                if not variant:
                    messages.error(
                        request,
                        f"The selected variant for {order_item.product.name} "
                        "is no longer available."
                    )
                    return redirect("vieworder", orderid=orderid)

                if variant.stock < order_item.quantity:
                    messages.error(
                        request,
                        f"Insufficient stock for {order_item.product.name} "
                        f"({variant.variant_name}). Available: {variant.stock}."
                    )
                    return redirect("vieworder", orderid=orderid)

                stock_records.append(
                    ("variant", variant, order_item.quantity)
                )

            else:

                product = Product.objects.select_for_update().get(
                    product_code=order_item.product_id
                )

                # A product with variants must have a selected variant.
                if ProductVariant.objects.filter(product=product).exists():
                    messages.error(
                        request,
                        f"Please select a variant for {product.name}. "
                        "This order needs to be recreated from your cart."
                    )
                    return redirect("cart")

                if product.stock < order_item.quantity:
                    messages.error(
                        request,
                        f"Insufficient stock for {product.name}. "
                        f"Available: {product.stock}."
                    )
                    return redirect("vieworder", orderid=orderid)

                stock_records.append(
                    ("product", product, order_item.quantity)
                )

        # All lines passed validation. Now deduct stock.
        for record_type, record, quantity in stock_records:
            record.stock -= quantity
            record.save(update_fields=["stock"])

        # Store payment method if your Order model has this field.
        # Add payment_method to the model before uncommenting this line.
        # order_obj.payment_method = "cod"

        order_obj.status = "placed"
        order_obj.updated_date = timezone.now()

        order_obj.save(
            update_fields=["status", "updated_date"]
        )

        CartItem.objects.filter(
            user=request.user,
            related_order=orderid
        ).delete()

    messages.success(request, "Order placed successfully!")
    return redirect("vieworder", orderid=orderid)

@login_required
@require_POST
def cancelorder(request, orderid):
    with transaction.atomic():
        order_obj = get_object_or_404(
            Order.objects.select_for_update(),
            order_id=orderid,
            user=request.user
        )

        if order_obj.status not in ("created", "placed"):
            messages.error(request, "This order cannot be cancelled.")
            return redirect("vieworder", orderid=orderid)

        elapsed = timezone.now() - order_obj.created_date

        if elapsed > timedelta(hours=2):
            messages.error(
                request,
                "The cancellation window has expired."
            )
            return redirect("vieworder", orderid=orderid)

        # Restore inventory only for an order that was actually placed.
        if order_obj.status == "placed":
            order_items = OrderItem.objects.filter(
                order=order_obj
            ).select_related("product", "variant")

            for item in order_items:
                if item.variant_id:
                    variant = ProductVariant.objects.select_for_update().filter(
                        id=item.variant_id,
                        product=item.product
                    ).first()

                    if variant:
                        variant.stock += item.quantity
                        variant.save(update_fields=["stock"])
                    else:
                        logger.error(
                            "Cannot restore stock: variant %s for order %s "
                            "no longer exists.",
                            item.variant_id,
                            orderid
                        )
                else:
                    product = Product.objects.select_for_update().get(
                        product_code=item.product_id
                    )
                    product.stock += item.quantity
                    product.save(update_fields=["stock"])

        order_obj.status = "cancelled"
        order_obj.updated_date = timezone.now()
        order_obj.save(update_fields=["status", "updated_date"])

        CartItem.objects.filter(
            user=request.user,
            related_order=orderid
        ).delete()

    messages.success(request, "Your order has been cancelled.")
    return redirect("vieworder", orderid=orderid)

@login_required
@require_POST
def changeDeliveryAdd(request, orderid):
    order_obj = get_object_or_404(
        Order,
        order_id=orderid,
        user=request.user
    )

    # Only allow address changes before confirmation
    if order_obj.status != "created":
        messages.error(
            request,
            "The delivery address can only be changed before order confirmation."
        )
        return redirect("vieworder", orderid=orderid)

    new_address = request.POST.get("delivery_address", "").strip()

    if not new_address:
        messages.error(request, "Please enter a delivery address.")
        return redirect(request.META.get(
            "HTTP_REFERER",
            reverse("vieworder", kwargs={"orderid": orderid})
        ))

    order_obj.delivery_address = new_address
    order_obj.save(update_fields=["delivery_address"])

    messages.success(
        request,
        "Delivery address updated successfully."
    )

    return redirect(request.META.get(
        "HTTP_REFERER",
        reverse("vieworder", kwargs={"orderid": orderid})
    ))

@login_required
def vieworder(request, orderid):

    # Fetch order belonging to the logged-in user
    order_obj = get_object_or_404(
        Order,
        order_id=orderid,
        user=request.user
    )

    # Fetch order items with product and variant details
    order_items = (
        OrderItem.objects.filter(order=order_obj)
        .select_related("product", "variant")
        .order_by("id")
    )

    # Calculate cancellation eligibility
    elapsed = timezone.now() - order_obj.created_date

    cancel_allowed = (
        elapsed <= timedelta(hours=2)
        and order_obj.status in ("created", "placed")
    )

    # Get user profile
    profile = UserProfile.objects.filter(
        user=request.user
    ).first()

    return render(
        request,
        "ecommstore/templates/orderdetails.html",
        {
            "order": order_obj,
            "order_items": enumerate(order_items),

            # Price details
            "orderamount": order_obj.subtotal,
            "shippingcharge": order_obj.shipping_charge,
            "grandtotal": order_obj.amount,

            # Cancellation
            "cancel_allowed": cancel_allowed,

            # Profile
            "profilepicture": (
                profile.profile_picture if profile else ""
            ),
        }
    )

def search_products(request):
    query = request.GET.get('q')
    results = []
    userprofile = UserProfile.objects.filter(user=request.user)
    profilepicture = ''
    if len(userprofile) > 0:
        profilepicture = userprofile[0].profile_picture
    images = [
        '/static/fashion25.png',
        '/static/fashiongirl.png',       
        '/static/fashion10.png',
    ]
    
    if query:
        results = Product.objects.filter(
            Q(name__icontains=query)|
            Q(description__icontains=query)|
            Q(category__icontains=query)|
            Q(desc1__icontains=query)
        ).distinct()
        return render(request,'ecommstore/templates/shop.html',{'products':results,'query':query,'images': images,'profilepicture':profilepicture})
    else:
        results = Product.objects.filter()
        return render(request,'ecommstore/templates/base.html',{'products': results,'images': images,'profilepicture':profilepicture})

def updateMyInfo(request):
    username = request.POST.get("Username")
    email = request.POST.get("Email")
    firstName= request.POST.get("FirstName")
    lastName= request.POST.get("LastName")
    address= request.POST.get("Address")
    profilepic= request.POST.get("profilepic") 

    #user = User.objects.filter(username=username)
    user = get_object_or_404(User, username=username)
    print("User:",user)
    user.email = email
    user.first_name = firstName
    user.last_name = lastName
    user.save()
    userprofile = get_object_or_404(UserProfile, user=user)
    userprofile.address = address
    if(profilepic!=None):
        userprofile.profile_picture = profilepic
        print(userprofile.profile_picture)
    userprofile.save()
    print(userprofile)
    messages.success(request,"Your info updated successfully!")
    # return HttpResponse("Updated successfully")
    return redirect("account")

@login_required
def view_order(request, order_id):
    order_obj = get_object_or_404(
        Order.objects.prefetch_related(
            "orderitem_set__product"
        ),
        order_id=order_id,
        user=request.user,
    )

    return render(
        request,
        "ecommstore/templates/orderdetails.html",
        {"order": order_obj},
    )
