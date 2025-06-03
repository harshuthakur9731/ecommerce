from django.shortcuts import render
from .models import Product,CartItem
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def home(request):
    products = Product.objects.all()
    images = [
        '/static/fashion25.png',
        '/static/fashiongirl.png',       
        '/static/fashion10.png'
    ]
    return render(request,'ecommstore/templates/base.html',{'products': products,'images': images})

def shop(request):
    return render(request,'ecommstore/templates/base.html')

def account(request):
    return render(request,'ecommstore/templates/base.html')

def logout(request):
    return render(request,'ecommstore/templates/base.html')

def login(request):
    return render(request,'ecommstore/templates/base.html')

def signup(request):
    return render(request,'ecommstore/templates/base.html')

def itemdetail(request,PCode):
    product = Product.objects.filter(product_code=PCode).values()
    print(product) 
    params = {
        "product_code":product[0]["product_code"],
        "name":product[0]["name"],
        "image":product[0]["image"],
        "description":product[0]["description"],
        "price":product[0]["price"],
        "instock":product[0]["stock"],
        "specifications":product[0]["specification"],
        "termsnconditions":product[0]["termsnconditions"],
        "desc1":product[0]["desc1"],
        "image1":product[0]["image1"],
        "image2":product[0]["image2"],
        "image3":product[0]["image3"],
        "images":[product[0]["image"],product[0]["image1"],product[0]["image2"],product[0]["image3"]]  
    }   
    return render(request,'ecommstore/templates/itemdetail.html',params)

def cart(request):
    cart_items = {}
    i=0
    final_cart_items = CartItem.objects.filter(user=request.user)
    cartlength = len(final_cart_items)

    for i in range(0,cartlength):
        cart_items[i] = final_cart_items[i]

    print(cart_items)
    return render(request,'ecommstore/templates/cartdetail.html',{'cart_items':cart_items.items()})

def resetcart(request):
    cartItemsTodel = CartItem.objects.filter(user=request.user)
    print('CartItem to delete for reset',cartItemsTodel)
    cartItemsTodel.delete()
    return render(request,'ecommstore/templates/cartdetail.html')

def addToCartAct(request,PCode):
    print("Hello World!",PCode)
    productInstance = Product.objects.filter(product_code=PCode)
    fetchedCartItem = CartItem.objects.filter(user=request.user,product=productInstance[0])
    if(len(fetchedCartItem)>0):
        print("Step 1")
        #item is already into the cart
        fetchedCartItem[0].quantity= fetchedCartItem[0].quantity + 1
        fetchedCartItem[0].price = productInstance[0].price
        fetchedCartItem[0].save()
    else:
        #new item added to the cart
        print("Step 2")
        cartProduct = CartItem(user=request.user,product=productInstance[0],price=productInstance[0].price)
        cartProduct.save()

    cart_items = {}
    i=0
    final_cart_items = CartItem.objects.filter(user=request.user)
    cartlength = len(final_cart_items)

    for i in range(0,cartlength):
        cart_items[i] = final_cart_items[i]

    print(cart_items)
    return render(request,'ecommstore/templates/cartdetail.html',{'cart_items':cart_items.items()})

def delToCartAct(request,itemid):
    fetchedCartItem = CartItem.objects.filter(user=request.user,id=itemid)
    print('CartItem to delete',fetchedCartItem)
    fetchedCartItem.delete()
    cart_items = {}
    i=0
    final_cart_items = CartItem.objects.filter(user=request.user)
    cartlength = len(final_cart_items)

    for i in range(0,cartlength):
        cart_items[i] = final_cart_items[i]

    print(cart_items)
    return render(request,'ecommstore/templates/cartdetail.html',{'cart_items':cart_items.items()})

