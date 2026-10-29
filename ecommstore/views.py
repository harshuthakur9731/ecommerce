from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from .models import Product,CartItem,UserProfile,Order,OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
import logging
import uuid
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
    ).order_by("-created_date")

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
        },
    )


@login_required
def cart(request):
    cart_items = list(
        CartItem.objects
        .filter(user=request.user)
        .select_related("product", "variant")
    )

    total_amount = Decimal("0")

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
            "cart_items": enumerate(cart_items),
            "total_amount": total_amount,
            "profilepicture": (
                profile.profile_picture if profile else ""
            ),
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
    product = get_object_or_404(
        Product,
        product_code=PCode,
    )

    item = CartItem.objects.filter(
        user=request.user,
        product=product,
        variant__isnull=True,
    ).first()

    if item:
        item.quantity += 1
        item.price = product.price
        item.save()
    else:
        CartItem.objects.create(
            user=request.user,
            product=product,
            quantity=1,
            price=product.price,
            related_order="",
        )

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
        .select_related("product")
        .order_by("id")
    )

    total_amount = sum(
        (item.amount for item in cart_items),
        Decimal("0.00"),
    )

    profile = UserProfile.objects.filter(user=user).first()

    return {
        "cart_items": enumerate(cart_items),
        "total_amount": total_amount,
        "profilepicture": (
            profile.profile_picture if profile else ""
        ),
    }

@login_required
@require_POST
def order(request):
    cart_items = list(
        CartItem.objects
        .filter(user=request.user)
        .select_related("product")
        .order_by("id")
    )

    if not cart_items:
        messages.warning(request, "Your cart is empty.")
        return redirect("cart")

    with transaction.atomic():
        order_id = f"ODR-{uuid.uuid4().hex.upper()}"

        new_order = Order.objects.create(
            order_id=order_id,
            user=request.user,
            status="created",
        )

        order_lines = []
        order_amount = Decimal("0.00")

        for item in cart_items:
            unit_price = item.price
            line_amount = unit_price * item.quantity

            order_lines.append(
                OrderItem(
                    order=new_order,
                    product=item.product,
                    quantity=item.quantity,
                    unitprice=unit_price,
                    amount=line_amount,
                )
            )

            order_amount += line_amount

        OrderItem.objects.bulk_create(order_lines)

        new_order.amount = order_amount
        new_order.save(update_fields=["amount"])

        CartItem.objects.filter(
            user=request.user,
            id__in=[item.id for item in cart_items],
        ).update(related_order=order_id)

    order_items = OrderItem.objects.filter(
        order=new_order
    ).select_related("product")

    return render(
        request,
        "ecommstore/templates/ordersummary.html",
        {
            "order_items": enumerate(order_items),
            "orderamount": order_amount,
            "order": new_order.order_id,
        },
    )


@login_required
@require_POST
def confirmorder(request, orderid):
    with transaction.atomic():
        order_obj = get_object_or_404(
            Order.objects.select_for_update(),
            order_id=orderid,
            user=request.user,
        )

        if order_obj.status != "created":
            messages.warning(
                request,
                "This order cannot be confirmed in its current state.",
            )
            return redirect("view_order", order_id=orderid)

        order_obj.status = "placed"
        order_obj.updated_date = timezone.now()
        order_obj.save(
            update_fields=["status", "updated_date"]
        )

        CartItem.objects.filter(
            user=request.user,
            related_order=orderid,
        ).delete()

    messages.success(request, "Order placed successfully!")
    return redirect("account")

@login_required
@require_POST
def cancelorder(request, orderid):
    with transaction.atomic():
        order = get_object_or_404(
            Order.objects.select_for_update(),
            order_id=orderid,
            user=request.user,
        )

        # Prevent cancellation of already-finalized orders.
        if order.status in ("cancelled", "placed"):
            messages.error(
                request,
                "This order cannot be cancelled."
            )
            return redirect("vieworder", orderid=order.order_id)

        # Allow cancellation within two hours of order creation.
        elapsed = timezone.now() - order.created_date

        if elapsed > timedelta(hours=2):
            messages.error(
                request,
                "The cancellation window has expired."
            )
            return redirect("vieworder", orderid=order.order_id)

        order.status = "cancelled"
        order.updated_date = timezone.now()
        order.save(update_fields=["status", "updated_date"])

        # Remove cart rows associated with this order, if present.
        CartItem.objects.filter(
            user=request.user,
            related_order=order.order_id,
        ).delete()

    messages.success(request, "Your order has been cancelled.")
    return redirect("vieworder", orderid=order.order_id)

def changeDeliveryAdd(request,orderid):
    order = Order.objects.filter(order_id=orderid)
    print('Order:',order)
    print("Delivery address chnaged")
    return cart(request)

def vieworder(request,orderid):
    order = Order.objects.filter(order_id=orderid)
    print('Order:',order)
    orderitems = OrderItem.objects.filter(order=order[0].order_id)
    print('OrderItems:',orderitems)
    finalorderitems = {}
    for i in range(0,len(orderitems)):
        finalorderitems[i] = orderitems[i]
    orderamount = order[0].amount
    time_diff = timezone.now()-order[0].updated_date
    two_hours = timedelta(hours=2)
    if time_diff <= two_hours and order[0].status != "cancelled":
        cancel_allowed = 1
        print("The time difference is less than or equal to 2 hours.")
    else:
        cancel_allowed = 0
        print("The time difference is greater than 2 hours.")
    print("time_diff",time_diff)

    userprofile = UserProfile.objects.filter(user=request.user)
    profilepicture = ''
    if len(userprofile) > 0:
        profilepicture = userprofile[0].profile_picture

    return render(request,'ecommstore/templates/orderdetails.html',{"order":order[0],"order_items":finalorderitems.items(),"orderamount":orderamount,"cancel_allowed":cancel_allowed,"profilepicture":profilepicture})

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
