from django.shortcuts import redirect, render

from django.contrib import messages
from .models import Product

# Create your views here.
def product_create(request):
    if request.method == "POST": # post ko được viết chữ thường
        # lấy theo tên input trong file html
        name            = request.POST['name'] # tên của input thêm hàng hóa tên là name <input type="text" class="form-control" name="name" required> trong file html
        price_purchase  = float(request.POST['purchase_price'])
        price_selling   = float(request.POST['selling_price'])
        quantity        = int(request.POST['quantity'])# bên trái là tên biến mình đặt phải trùng với tên biến trong files models.py nha , bên phải là tên imput đầu vào

        item_product = Product(name = name, price_purchase = price_purchase, price_selling = price_selling, quantity = quantity)
        item_product.save() # lưu lại khi thêm sản phẩm
        
        messages.success(request, 'Sản phẩm đã được tạo thành công')
        
        return redirect('/') # chuyển hướng về trang list không có path
         
    return render(request,'product_create.html',{}) # bien thuc 3 la contact, bien thuc 2 la template
    # nếu phương thức là get là gọi request để thêm sản phẩm
    

def product_list(request):
    items_product = Product.objects.all() #lấy toàn bộ phần tử trong db
    
    total_revenue = sum(product.price_selling * product.quantity_sold for product in items_product)
    
    total_profit = sum((product.price_selling- product.price_purchase)* product.quantity_sold for product in items_product)
    
    return render(request,'product_list.html',{
        'nhung_san_pham': items_product,
        'doanh_thu': total_revenue,
        'loi_nhuan': total_profit
    }) 

def product_update(request,product_id):
    
    #lấy id của product từ db
    item_sanpham = Product.objects.get(id = product_id) # lấy từ item_product dưới
    
    if request.method == "POST": # post ko được viết chữ thường
        # lấy theo tên input trong file html
        item_sanpham.name            = request.POST['name'] # tên của input thêm hàng hóa tên là name <input type="text" class="form-control" name="name" required> trong file html
        item_sanpham.price_purchase  = float(request.POST['purchase_price'])
        item_sanpham.price_selling   = float(request.POST['selling_price'])
        item_sanpham.quantity        = int(request.POST['quantity'])# bên trái là tên biến mình đặt phải trùng với tên biến trong files models.py nha , bên phải là tên imput đầu vào
        item_sanpham.quantity_sold   = int(request.POST['sold_quantity'])
        
        item_sanpham.save() # lưu lại khi thêm sản phẩm
        
        messages.success(request, 'Sản phẩm đã được câp nhật thành công')
        
        return redirect('/') # chuyển hướng về trang list không có path
    
    return render(request,'product_update.html',{"san_pham": item_sanpham}) 

def product_delete(request,product_id):
    
    #lấy id của product từ db
    item_xoa = Product.objects.get(id = product_id) # lấy từ item_product dưới
    item_xoa.delete()
    
    messages.success(request, 'Sản phẩm đã được xóa thành công')
        
    return redirect('/')


def product_sell(request,product_id):
    
    #lấy id của product từ db
    item_sell = Product.objects.get(id = product_id) # lấy từ item_product dưới
    
    quantity_sell = int(request.GET.get('quantity'))
    
    item_sell.quantity -= quantity_sell
    item_sell.quantity_sold += quantity_sell
    item_sell.save()
    
    messages.success(request, 'Sản phẩm đã bán thành công')
        
    return redirect('/')