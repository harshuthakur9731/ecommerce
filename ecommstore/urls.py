from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.login,name="login"),
    path('home',views.home,name="home"),
    path('shop',views.home,name="shop"),
    path('cart',views.home,name="cart"),
    path('account',views.home,name="account"),
    path('logout',views.home,name="logout"),
    path('login',views.home,name="login"),
    path('signup',views.home,name="signup"),
    path('itemdetail/<slug:PCode>',views.itemdetail,name="itemdetail"),
]
