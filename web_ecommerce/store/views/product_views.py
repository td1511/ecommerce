from django.shortcuts import render, redirect
from store.forms import ProductForm
from store.models import Product, Category, User, Cart, CartItem
 # Import model Product
from django.shortcuts import render, get_object_or_404
from store.models import Product, ProductImage

from django.contrib import messages  # dùng để hiển thị thông báo


'''def create_product(request): 
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            
            # Gán người tạo sản phẩm
            user_id = request.session.get('user_id')
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    product.user = user
                except User.DoesNotExist:
                    pass
            if not product.quantity_sold:
                product.quantity_sold = 0
            product.save()
            return redirect('home')  # Điều hướng về danh sách sản phẩm
    else:
        form = ProductForm()

    categories = Category.objects.all()

    return render(request, 'add_product.html', {
        'form': form,
        'categories': categories
    })
'''


def product_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')

    categories = Category.objects.all()

    # Nếu là người bán
    if request.session.get('user_name') and request.session.get('role') == 'seller':
        try:
            user = User.objects.get(name=request.session.get('user_name'))
        except User.DoesNotExist:
            user = None

        products = Product.objects.filter(user=user)

        total_revenue = sum((p.price_selling or 0) * (p.quantity_sold or 0) for p in products)
        total_profit = sum(((p.price_selling or 0) - (p.price_purchase or 0)) * (p.quantity_sold or 0) for p in products)


        return render(request, 'product_list_seller.html', {
            'products': products,
            'total_revenue': total_revenue,
            'total_profit': total_profit,
        })

    # Người dùng thông thường
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

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})


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

'''def add_to_cart(request, product_id):
    
    
    product = get_object_or_404(Product, id=product_id)

    
    cart = request.session.get('cart', {})  # Lấy giỏ hàng từ session, nếu chưa có thì là dict rỗng

    # Nếu sản phẩm đã có trong giỏ, tăng số lượng lên 1
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': float(product.price_selling),
            'quantity': 1,
        }

    request.session['cart'] = cart  # Lưu lại giỏ hàng vào session
    request.session.modified = True  # Đánh dấu session đã thay đổi

    return redirect('home')  # Chuyển hướng về trang chủ hoặc nơi bạn muốn

'''
from django.contrib import messages



'''def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if product.quantity_left == 0:
        messages.error(request, f"Sản phẩm '{product.name}' đã hết hàng.")
        return render(request, '', {'products': Product.objects.all()})

    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': float(product.price_selling),
            'quantity': 1,
        }

    request.session['cart'] = cart
    request.session.modified = True

    messages.success(request, f"Đã thêm '{product.name}' vào giỏ hàng.")
    return render(request, '', {'products': Product.objects.all()})'''



def add_to_cart(request, product_id):

    user_id = request.session.get('user_id')
    role = request.session.get('role')

    if not user_id or not role:
        return render(request, 'login.html')
    product = get_object_or_404(Product, id=product_id)
    if product.quantity_left == 0:
        
        messages.error(request, f"Sản phẩm '{product.name}' đã hết hàng.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
        
        
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': float(product.price_selling),
            'quantity': 1,
        }

    request.session['cart'] = cart
    request.session.modified = True
    
    messages.success(request, f"Đã thêm '{product.name}' vào giỏ hàng.")
    return redirect(request.META.get('HTTP_REFERER', '/'))



from django.shortcuts import render, get_object_or_404, redirect
from store.models import Product
from store.forms import ProductForm

# View sửa sản phẩm
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

# View xóa sản phẩm
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'confirm_delete.html', {'product': product})
