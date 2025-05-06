from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

# biến đầu tiên là mình tự đặt để hiển thị trên trang web, biến thứ 2 phải lấy từ views, biến thứ 3 cũng có thể là tên từ biến 1 hoặc lấy tên khác : sẽ thêm tên ở biến thứ 3 vào link html

urlpatterns = [
    
    path('', views.home, name='home'),
    
    path("logup/", views.logup_view, name="logup"),  
    
    path('login/', views.login_view, name= "login"),
    
    path('logout/', views.logout_view, name='logout'),
    
    path('password-reset/', views.password_reset_view, name='password_reset'),
    
    # thêm sản phẩm 
    path('add_product/', views.add_product, name='product_add'),
    
    # thêm danh mục sản phẩm
    path("category/add_category/", views.add_category_view, name="add_category"),
    
    # thêm vào giỏ hàng 
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    
    # danh sách sản phẩm cả người mua, người bán đều xem được
    path('product_list/', views.product_list, name='product_list'),  
    
    # danh sách sản phẩm theo shop chỉ người bán xem
    path('product_list_seller/', views.product_list_seller, name='product_list_seller'),
    
    #khi clicks vào 1 sản phẩm để xem chi tiết thông tin sản phẩm
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    
    # hiển thị chi tiết giỏ hàng
    path('cart/', views.cart_detail, name='cart_detail'),

    # xử lý khi tăng, giảm số lượng hoặc xóa mặt hàng khỏi giỏ hàng
    path('cart/update/', views.update_cart, name='update_cart'),
    
    # thông tin đơn hàng sau khi click mua hàng trên giỏ
    path('checkout/', views.checkout, name='checkout'),
    
    #lịch sử mua hàng với cả người mua và người bán
    path('order-history/', views.order_history, name='order_history'),
    
    #liịch sử phê duyệt đơn hàng với người bán
    path('order-approval/', views.order_approval, name='order_approval'),
    
    #hiện thị thông tin tab 
    path('orders/approve/<int:order_id>/', views.approve_order, name='approve_order'),
    
    path('orders/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    
    path('orders/delivered/<int:order_id>/', views.mark_delivered, name='mark_delivered'),
    
    #hiển thị trang sửa thông tin sản phẩm với người bán 
    path('products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    
    #hiển thị trang xóa sản phẩm với người bán
    path('products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
] 
 
if settings.DEBUG:
    #để thêm ảnh từ máy lên
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # hiển thị ảnh khi thêm vào folder sẵn
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)