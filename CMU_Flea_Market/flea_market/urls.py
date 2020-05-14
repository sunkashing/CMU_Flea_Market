"""webapps URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib.auth.decorators import login_required
from django.urls import include, path
from flea_market import views

urlpatterns = [
    path('', views.login_action, name='login'),
    path('logout', views.logout_action, name='logout'),
    path('index/<str:category>', views.index_action, name='index'),
    path('sort_by_price_asc/<str:category>', views.sort_by_price_asc, name='sort_by_price_asc'),
    path('sort_by_price_desc/<str:category>', views.sort_by_price_desc, name='sort_by_price_desc'),
    path('sort_by_distance/<str:category>', views.sort_by_distance, name='sort_by_distance'),
    path('sort_by_popularity/<str:category>', views.sort_by_popularity, name='sort_by_popularity'),
    path('register', views.register_action, name='register'),
    path('order', views.order_action, name='order'),
    path('author', views.author_action, name='author'),
    path('customer_photo/<int:id>', views.get_customer_photo, name='customer_photo'),
    path('product/<int:item_id>', views.product_action, name='product'),
    path('post/<int:id>', views.post_action, name='post'),
    path('item-photo/<int:id>', views.get_item_photo, name='item-photo'),
    path('update_cust_info', views.update_cust_info, name='update_cust_info'),
    path('update_location', views.update_location, name='update_location'),
    path('category_photo/<str:cat_str>', views.get_category_photo, name='category_photo'),
    path('order/<int:item_id>', views.order_action, name='creat_order'),
    path('payment/canceled', views.payment_canceled, name='payment_cancel'),
    path('payment/payment_done/<int:tran_id>', views.payment_done, name='payment_done'),
    path('seller-page/<int:item_id>', views.contact_seller_action, name='seller_page'),
    path('buyer-page/<int:item_id>', views.contact_buyer_action, name='buyer_page'),
    path('search', views.MySearchIndex.as_view(), name='search'),
    path('follow_action', views.follow_action, name='follow'),
    path('favorite', views.favorite_action, name='favorite'),
    path('item-photo-list/<int:id>', views.get_item_photo_list, name='get-item-photo-list'),
    path('delete-item/<int:id>', views.delete_action, name='delete_item')
]