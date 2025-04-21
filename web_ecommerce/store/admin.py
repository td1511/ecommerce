from django.contrib import admin


# Register your models here.
from .models import User, Category, Product, Address, Order, OrderItem, Cart,CartItem,ProductImage # Import model

# Đăng ký model vào admin
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

admin.site.register(Product, ProductAdmin)