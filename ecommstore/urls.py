from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    
    # Custom login and logout
    path('login/', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('',views.home,name="home"),
    path('signup',views.signup,name="signup"),
    path('shop',views.shop,name="shop"),
    path('search_products',views.search_products,name="search_products"),
    path('cart',views.cart,name="cart"),
    path('resetCart',views.resetcart,name="resetCart"),
    path('addToCartAct/<slug:PCode>',views.addToCartAct,name="addToCartAct"),
    path('delToCartAct/<slug:itemid>',views.delToCartAct,name="delToCartAct"),
    path('account',views.account,name="account"),
    path('itemdetail/<slug:PCode>',views.itemdetail,name="itemdetail"),
    path('order',views.order,name="order"),
    path('confirmorder/<slug:orderid>',views.confirmorder,name="confirmorder"),
    path('cancelorder/<slug:orderid>',views.cancelorder,name="cancelorder"),
    path('vieworder/<slug:orderid>',views.vieworder,name="vieworder"),
    #path('vieworder/cancelorder/<slug:orderid>',views.cancelorder,name="cancelorder"),
]
