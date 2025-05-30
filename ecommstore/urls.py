from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Custom login and logout
    path('', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True, next_page='/home'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

   # path('',views.home,name="login"),
    path('home',views.home,name="home"),
    path('shop',views.home,name="shop"),
    path('cart',views.cart,name="cart"),
    path('resetCart',views.resetcart,name="resetCart"),
    path('addToCartAct/<slug:PCode>',views.addToCartAct,name="addToCartAct"),
    path('delToCartAct/<slug:itemid>',views.delToCartAct,name="delToCartAct"),
    path('account',views.home,name="account"),
    path('admin/logout',views.logout,name="logout"),
    path('home',views.home,name="login"),
    path('signup',views.home,name="signup"),
    path('itemdetail/<slug:PCode>',views.itemdetail,name="itemdetail"),
]
