from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Cart, CartItem, User
from django.contrib import messages

# view khi click vào các nút thêm vào giỏ
def add_to_cart(request, product_id):
    user_id = request.session.get('user_id')
    role = request.session.get('role')

    if not user_id or not role:
        messages.warning(request, "Vui lòng đăng nhập để thêm sản phẩm vào giỏ hàng.")
        return redirect('login')  # hoặc render ra login.html

    print(user_id)
    
    product = get_object_or_404(Product, id=product_id)

    if product.quantity_left == 0:
        messages.error(request, f"Sản phẩm '{product.name}' đã hết hàng.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # --- PHẦN 1: LƯU VÀO SESSION ---
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

    # --- PHẦN 2: LƯU VÀO DATABASE ---
    #from django.contrib.auth import get_user_model
    #User = get_user_model()
    user = get_object_or_404(User, id=user_id)

    # Lấy hoặc tạo Cart cho user
    cart_db, created = Cart.objects.get_or_create(user=user)

    # Lấy hoặc tạo CartItem
    cart_item, created = CartItem.objects.get_or_create(cart=cart_db, product=product)
    if not created:
        cart_item.quantity += 1
    else:
        cart_item.quantity = 1
    cart_item.save()

    messages.success(request, f"Đã thêm '{product.name}' vào giỏ hàng.")
    return redirect(request.META.get('HTTP_REFERER', '/'))


# hiển thị trên trang cart.html
def cart_detail(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for product_id, item_data in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            quantity = item_data.get('quantity', 1)
            subtotal = product.price_selling * quantity
            total += subtotal

            items.append({
                'id': product.id,
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
        except Product.DoesNotExist:
            continue

    return render(request, 'cart.html', {'items': items, 'total': total})




def update_cart(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        action = request.POST.get('action')

        if action:
            try:
                action_type, product_id = action.split('-')
                product_id = str(product_id)
                product_id_int = int(product_id)  # Dùng cho DB
            except ValueError:
                return redirect('cart_detail')

            # SESSION xử lý
            if action_type == 'increase':
                if product_id in cart:
                    cart[product_id]['quantity'] += 1
                else:
                    # Nếu sản phẩm chưa có, thêm mới (tuỳ bạn muốn cho phép không)
                    cart[product_id] = {'quantity': 1, 'name': 'Tên sản phẩm', 'price': 0}

            elif action_type == 'decrease':
                if product_id in cart:
                    if cart[product_id]['quantity'] > 1:
                        cart[product_id]['quantity'] -= 1
                    else:
                        del cart[product_id]

            elif action_type == 'remove':
                if product_id in cart:
                    del cart[product_id]

            # CẬP NHẬT SESSION
            if cart:
                request.session['cart'] = cart
            else:
                request.session.pop('cart', None)

            request.session.modified = True

            # CẬP NHẬT DATABASE
            user_id = request.session.get('user_id')
            if user_id:
                user = get_object_or_404(User, id=user_id)
                try:
                    cart_db = Cart.objects.get(user=user)

                    cart_item_qs = CartItem.objects.filter(cart=cart_db, product_id=product_id_int)
                    cart_item = cart_item_qs.first() if cart_item_qs.exists() else None

                    if action_type == 'increase':
                        if cart_item:
                            cart_item.quantity += 1
                            cart_item.status = 'active'
                            cart_item.save()
                        else:
                            CartItem.objects.create(
                                cart=cart_db,
                                product_id=product_id_int,
                                quantity=1,
                                status='active'
                            )

                    elif action_type == 'decrease':
                        if cart_item:
                            if cart_item.quantity > 1:
                                cart_item.quantity -= 1
                                cart_item.save()
                            elif cart_item.quantity == 1:
                                cart_item.quantity = 0
                                cart_item.status = 'removed'
                                cart_item.save()

                    elif action_type == 'remove':
                        if cart_item:
                            cart_item.quantity = 0
                            cart_item.status = 'removed'
                            cart_item.save()

                except Cart.DoesNotExist:
                    pass


    return redirect('cart_detail')



