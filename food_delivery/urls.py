"""
URL configuration for food_delivery project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from food_delivery_app import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('', views.test_mysql),
    path('restaurants/', views.restaurant_list, name='restaurant_list'),
    # TODO: account path needs to take customer_id as 'profile/<customer_id>'
    path('profile/', views.account_view, name='account'),

    # TODO: order history path needs to take customer_id as 'order_history/<customer_id>'
    path('order_history/<str:customer_id>/', views.order_history_view, name='order_history'),
    path('restaurants/<str:restaurant_id>/', views.restaurant_menu, name='restaurant_menu'),
    path('cart/add/<str:res_id>/<str:item_name>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<str:item_key>/', views.update_cart, name='update_cart'),
    path('cart/', views.show_cart, name='show_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),

    path('', views.home, name='home'),

    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/<str:customer_id>/', views.profile, name='profile'),  # 动态用户 Profile 路由
]
