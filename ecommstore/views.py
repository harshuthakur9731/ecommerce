from django.shortcuts import render
from .models import Product

# Create your views here.
def login(request):
    products = Product.objects.all()
    return render(request,'admin/login/?next=/admin/',{'products': products})

def home(request):
    products = Product.objects.all()
    return render(request,'ecommstore/templates/base.html',{'products': products})

def shop(request):
    return render(request,'ecommstore/templates/base.html')

def cart(request):
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
    }   

    return render(request,'ecommstore/templates/itemdetail.html',params)