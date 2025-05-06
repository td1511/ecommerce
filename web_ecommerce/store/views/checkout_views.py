from django.shortcuts import render, redirect, get_object_or_404
from store.models import User, Product, Order, OrderItem, Address
from decimal import Decimal
from django.utils import timezone
from django.contrib import messages
from collections import defaultdict
from django.views.decorators.http import require_POST

# thông tin về đơn hàng : người mua, người bán , số lượng , địa chỉ
def checkout(request):
    user_id = request.session.get('user_id')
    role = request.session.get('role')

    if not user_id :
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return render(request, 'error.html', {'message': 'Không tìm thấy khách hàng!'})
    
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart_detail')

    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        payment_method = request.POST.get('payment_method')

        if address_id:
            address = get_object_or_404(Address, id=address_id)
        else:
            city = request.POST.get('city')
            district = request.POST.get('district')
            ward = request.POST.get('ward')
            street = request.POST.get('street')

            address = Address.objects.create(
                user=user,
                city=city,
                district=district,
                ward=ward,
                street=street,
            )

        # 👉 Gom sản phẩm theo người bán
        grouped_by_seller = defaultdict(list)
        for product_id, item in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                seller = product.user # hoặc product.user tùy theo model của bạn
                grouped_by_seller[seller].append((product, item))
            except Product.DoesNotExist:
                continue

        orders_created = []

        for seller, products in grouped_by_seller.items():
            total = Decimal('0')
            order = Order.objects.create(
                user=user,
                address=address,
                total_amount=0,
                shipping_fee=Decimal('0'),
                status='pending',
                payment_status='unpaid',
                payment_method=payment_method,
            )

            for product, item in products:
                quantity = item.get('quantity', 1)
                price = Decimal(item.get('price', product.price_selling or 0))
                subtotal = price * quantity

                if product.quantity_left < quantity:
                    return render(request, 'error.html', {
                        'message': f"Sản phẩm '{product.name}' không đủ hàng. Chỉ còn {product.quantity_left} sản phẩm."
                    })

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price_at_order=price,
                )

                product.quantity_left -= quantity
                product.quantity_sold += quantity
                product.save()

                total += subtotal

            order.total_amount = total
            order.save()
            orders_created.append(order)

        # Xoá giỏ hàng khỏi session
        request.session.pop('cart', None)
        request.session.modified = True

        return render(request, 'order_success.html', {'orders': orders_created})

    # GET request
    total = Decimal('0')
    selected_items = []

    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue

        quantity = item.get('quantity', 1)
        price = Decimal(item.get('price', product.price_selling or 0))
        subtotal = price * quantity
        total += subtotal

        selected_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    addresses = Address.objects.filter(user=user_id)
    user_info = user
    print(user_info)
    return render(request, 'checkout.html', {
        'selected_items': selected_items,
        'total': total,
        'addresses': addresses,
        'user_name': user_info.name,
        'user_phone': user_info.telephone,
    })



    
# lịch sử mua hàng với cả người mua và người bán
def order_history(request):
    user_id = request.session.get('user_id')
    role = request.session.get('role')

    if not user_id or not role:
        return render(request, 'login.html')
    
    # Xử lý lịch sử đơn hàng của khách hàng và người bán mua của người khác
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return render(request, 'error.html', {'message': 'Không tìm thấy khách hàng!'})

    orders = Order.objects.filter(user=user).order_by('-created_at')

    context = {
        'pending_orders': orders.filter(status='pending'),
        'shipping_orders': orders.filter(status='shipping'),
        'delivered_orders': orders.filter(status='delivered'),
        'cancelled_orders': orders.filter(status='cancelled'),
        'role': role,
    }
    return render(request, 'order_history.html', context)

# phê duyệt đơn hàng chỉ với người bán
def order_approval(request):
    user_id = request.session.get('user_id')
    role = request.session.get('role')

    if not user_id or not role:
        return render(request, 'login.html')
    if role == 'seller':
        # Xử lý danh sách đơn hàng cho người bán (ví dụ: tất cả đơn 'pending')
        orders = Order.objects.all().order_by('-created_at')

        # Phân loại theo trạng thái
        orders_to_approve = orders.filter(status='pending')
        shipping_orders = orders.filter(status='shipping')
        delivered_orders = orders.filter(status='delivered')

        context = {
            'orders_to_approve': orders_to_approve,
            'shipping_orders': shipping_orders,
            'delivered_orders': delivered_orders,
            'role': role,
        }
        return render(request, 'order_approval.html', context)

    else:
        messages.error(request, 'Vai trò không hợp lệ.')
        return redirect('login')
    

# để hiển thị từng tab khi phê duyệt đơn hàng/ lịch sử đơn hàng
@require_POST
def approve_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'shipping'
    order.save()
    messages.success(request, f"Đã phê duyệt đơn hàng #{order.id}.")
    return redirect('order_approval')

@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'cancelled'
    order.save()
    messages.warning(request, f"Đã huỷ đơn hàng #{order.id}.")
    return redirect('order_approval')

@require_POST
def mark_delivered(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'delivered'
    order.save()
    messages.success(request, f"Đã giao đơn hàng #{order.id}.")
    return redirect('order_approval')
