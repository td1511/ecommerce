from django.db import models
from django.conf import settings

# Create your models here.
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError

class User(models.Model):
    ROLE_CHOICES = [
        ('seller', 'Seller'),
        ('customer', 'Customer'),
    ]

    name = models.CharField(max_length=100)  # Tên người dùng
    telephone = models.CharField(max_length=15, unique=True)  # Số điện thoại, không trùng
    email = models.EmailField(unique=True)  # Email, không trùng lặp
    password = models.CharField(max_length=255)  # Mật khẩu, nên được mã hóa
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')  # Vai trò người dùng
    created_at = models.DateTimeField(auto_now_add=True)  # Thời gian tạo
    updated_at = models.DateTimeField(auto_now=True)  # Thời gian cập nhật

    def __str__(self):
        return f"{self.name} - {self.get_role_display()}"

    '''def set_password(self, raw_password):
        """Mã hóa mật khẩu trước khi lưu"""
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        """Kiểm tra mật khẩu nhập vào có đúng không"""
        return check_password(raw_password, self.password)'''

class Customer(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """Đảm bảo chỉ user có role là 'buyer' mới được tạo thành Customer"""
        if self.user.role != 'customer':
            raise ValidationError("Chỉ có User có role là 'customer' mới được tạo thành Customer")

    def save(self, *args, **kwargs):
        """Gọi clean() trước khi lưu"""
        self.clean() # đảm bảo chỉ customer mới được lưu hàm clean này là gọi hàm clean tự định nghĩa
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Customer: {self.user.name}"


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

# 4. Model Product
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    brand = models.TextField(blank=True, null=True)
    price_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    price_selling = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity_sold = models.PositiveIntegerField(default=0, blank=True, null=True)

    quantity_left = models.PositiveIntegerField(default=0)
    discount = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=True, blank=True, related_name='products_created')

    def __str__(self):
        return self.name

    @property
    def status(self):
        return "Còn hàng" if self.quantity_left > 0 else "Hết hàng"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return f"Ảnh của {self.product.name}"
    
# 5. Model Order
'''class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('shipped', 'Shipped'), ('completed', 'Completed')], default='pending')
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    payment_status = models.CharField(max_length=20, choices=[('unpaid', 'Unpaid'), ('paid', 'Paid')], default='unpaid')
    payment_method = models.CharField(max_length=20, choices=[('cash', 'Cash'), ('card', 'Card')], default='cash')

    def __str__(self):
        return f"Order {self.id} - {self.customer.user.username}"'''
        
'''class Address(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='addresses')
    recipient_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address_line = models.TextField()
    is_default = models.BooleanField(default=False)  # đánh dấu địa chỉ mặc định
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.recipient_name} - {self.address_line}"
    
'''
class Address(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='addresses')
    city = models.CharField(max_length=100, default= '')
    district = models.CharField(max_length=100, default= '')
    ward = models.CharField(max_length=100,default='')
    street = models.CharField(max_length=100, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.street}, {self.ward}, {self.district}, {self.city}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xác nhận'),
        ('shipping', 'Đang giao'),
        ('delivered', 'Đã giao'),
        ('cancelled', 'Đã huỷ'),
    ]

    PAYMENT_METHODS = [
        ('cash', 'Thanh toán khi nhận hàng'),
        ('card', 'Thẻ ngân hàng'),
    ]

    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    seller = models.ForeignKey('User', on_delete=models.CASCADE, null=True, blank=True, related_name='seller_orders')  # 👈 Thêm dòng này
    address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, default='unpaid')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.customer.user.name}"

    def save(self, *args, **kwargs):
        # Nếu đơn hàng đã có trong DB thì kiểm tra thay đổi trạng thái
        if self.pk:
            old_order = Order.objects.get(pk=self.pk)
            if old_order.status != self.status:
                self.handle_status_change(old_order.status, self.status)
        super().save(*args, **kwargs)

    def handle_status_change(self, old_status, new_status):
        order_items = self.orderitem_set.all()
        for item in order_items:
            product = item.product
            quantity = item.quantity

            # Nếu chuyển từ pending sang delivered -> trừ kho, cộng đã bán
            if old_status == 'pending' and new_status == 'delivered':
                product.quantity_left -= quantity
                product.quantity_sold += quantity

            # Nếu từ pending sang cancelled -> không giao hàng nữa => không trừ kho, không cộng đã bán
            elif old_status == 'pending' and new_status == 'cancelled':
                # Nếu đã từng trừ kho & cộng sold khi pending (ví dụ pending tự trừ kho), thì khôi phục
                product.quantity_left += quantity
                product.quantity_sold = max(product.quantity_sold - quantity, 0)

            # Nếu từ cancelled sang trạng thái khác (đơn khôi phục lại) => trừ kho
            elif old_status == 'cancelled' and new_status != 'cancelled':
                product.quantity_left -= quantity

            # Nếu từ trạng thái khác sang delivered (nhưng không phải từ pending)
            elif old_status != 'delivered' and new_status == 'delivered':
                product.quantity_sold += quantity

            product.save()


    
# 6. Model OrderItem
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)  # Giá tại thời điểm đặt hàng

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"
    
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Giỏ hàng của {self.user.name}"
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def subtotal(self):
        return self.product.price_selling * self.quantity
    




