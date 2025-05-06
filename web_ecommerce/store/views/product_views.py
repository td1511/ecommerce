from django.shortcuts import render, redirect, get_object_or_404
from store.forms import ProductForm
from store.models import Product, Category, User, ProductImage
from django.contrib import messages  # dùng để hiển thị thông báo

# View thêm sản phẩm mới
def add_product(request):
    if request.method == 'POST':
        # Lấy user_id từ session
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')  # Nếu chưa đăng nhập

        user = User.objects.get(id=user_id)

        # Lấy dữ liệu từ form
        name = request.POST.get('name')
        description = request.POST.get('description')
        brand = request.POST.get('brand')
        price_purchase = request.POST.get('price_purchase')
        price_selling = request.POST.get('price_selling')
        quantity_left = request.POST.get('quantity_left')
        discount = request.POST.get('discount')
        category_id = request.POST.get('category')

        # Tạo sản phẩm mới và gán người bán
        product = Product.objects.create(
            name=name,
            description=description,
            brand=brand,
            price_purchase=price_purchase,
            price_selling=price_selling,
            quantity_left=quantity_left,
            discount=discount,
            category_id=category_id,
            user=user  # 👈 Gán người bán ở đây
        )

        # ✅ Lưu nhiều ảnh
        images = request.FILES.getlist('images')
        for img in images:
            ProductImage.objects.create(product=product, image=img)

        return redirect('product_list')

    # GET method
    categories = Category.objects.all()
    return render(request, 'add_product.html', {'categories': categories})


# danh sách sản phẩm hiện thị theo tuwufng category
def product_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    categories = Category.objects.all()
    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    if category_id:
        products = products.filter(category_id=category_id)

    return render(request, 'product_list.html', {
        'products': products,
        'categories': categories,
        'query': query
    })

# danh sách sản phẩm của shop chỉ hiển thị với người bán để biết doanh thu lợi nhuận
def product_list_seller(request):
    query = request.GET.get('q', '')
    
    # Nếu là người bán thì đây là hiển thị thành dạnh bảng có doanh thu và lợi nhuận
    if request.session.get('user_name') and request.session.get('role') == 'seller':
        try:
            user = User.objects.get(id=request.session['user_id'])
        except User.DoesNotExist:
            user = None
        
        products = Product.objects.filter(user=user)
        if query:
            products = products.filter(name__icontains=query)
        total_revenue = sum((p.price_selling or 0) * (p.quantity_sold or 0) for p in products)
        total_profit = sum(((p.price_selling or 0) - (p.price_purchase or 0)) * (p.quantity_sold or 0) for p in products)


        return render(request, 'product_list_seller.html', {
            'products': products,
            'total_revenue': total_revenue,
            'total_profit': total_profit
        })

# chi tiết cho từng sản phẩm 
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})


# View sửa sản phẩm của người bán
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'edit_product.html', {'form': form, 'product': product})

# View xóa sản phẩm của người bán
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'confirm_delete.html', {'product': product})
