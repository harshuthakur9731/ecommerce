from django.shortcuts import render,redirect
from .models import Product,CartItem,UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

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

def signup(request):
    Name = request.POST.get("name")
    Email = request.POST.get("email")
    Pswd = request.POST.get("pswd")
    print('Hello')
    print('Name,Email,Pswd',Name+Email+Pswd)
    existingUsers = User.objects.filter(username=Name)
    if len(existingUsers)==0:
        user = User.objects.create_user(username=Name,password=Pswd,email=Email)
        user.save()
        messages.success(request,'Your Account has been created successfully!')
        return redirect('login')
    else:
        messages.success(request,'username already exists!')
        print('username already exists!')    
    return redirect('login')

def shop(request):
    return render(request,'ecommstore/templates/base.html')

def account(request):
    userprofile = UserProfile.objects.filter(user=request.user)
    profilepicture = ''
    if len(userprofile) > 0:
        profilepicture = userprofile[0].profile_picture
    return render(request,'ecommstore/templates/account.html',{'profilepicture':profilepicture})

def logout(request):
    return render(request,'ecommstore/templates/base.html')

def login(request):
    return render(request,'ecommstore/templates/base.html')

#def signup(request):
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

@login_required
def cart(request):
    cart_items = {}
    userprofile = UserProfile.objects.filter(user=request.user)
    profilepicture = ''
    if len(userprofile) > 0:
        profilepicture = userprofile[0].profile_picture
    i=0
    final_cart_items = CartItem.objects.filter(user=request.user)
    cartlength = len(final_cart_items)

    for i in range(0,cartlength):
        cart_items[i] = final_cart_items[i]

    print(cart_items)
    return render(request,'ecommstore/templates/cartdetail.html',{'cart_items':cart_items.items(),'profilepicture':profilepicture})

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


