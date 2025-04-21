from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

 # biến đầu tiên là mình tự đặt để hiển thị trên url, biến thứ 2 phải lấy từ views, biến thứ 3 cũng có thể là tên từ biến 1 hoặc lấy tên khác
urlpatterns = [
    path('', views.home, name='home'),
    
    path("logup/", views.logup_view, name="logup"),  # Đường dẫn đến view logup
    
    path('login/', views.login_view, name= "login"),
    
    path('logout/', views.logout_view, name='logout'),
    
    path('password-reset/', views.password_reset_view, name='password_reset'),
    
    # thêm sản phẩm 
    path('add/', views.add_product, name='product_add'),
    # thêm danh mục sản phẩm
    path("category/add/", views.add_category_view, name="add_category"),
    # thêm vào giỏ hàng 
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    # danh sách sản phẩm cả người mua, người bán đều xem được
    path('product_list/', views.product_list, name='product_list'),  # Đường dẫn để xem danh sách sản phẩm
    # danh sách sản phẩm theo shop chỉ người bán xem
    path('product_list_seller/', views.product_list_seller, name='product_list_seller'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    
    path('cart/', views.cart_detail, name='cart_detail'),
 
    #path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('cart/update/', views.update_cart, name='update_cart'),
    
    path('checkout/', views.checkout, name='checkout'),
    
    path('don-hang/', views.manage_orders, name='manage_orders'),

    path('order-history/', views.order_history, name='order_history'),
    
    path('order-approval/', views.order_approval, name='order_approval'),
    
    path('orders/approve/<int:order_id>/', views.approve_order, name='approve_order'),
    
    path('orders/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    
    path('orders/delivered/<int:order_id>/', views.mark_delivered, name='mark_delivered'),
    
    path('products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    
    path('products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
] 
 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)