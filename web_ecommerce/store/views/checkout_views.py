from django.shortcuts import render, redirect, get_object_or_404
from store.models import Customer, Product, Order, OrderItem, Address
from decimal import Decimal
from django.utils import timezone
from django.contrib import messages

'''def checkout(request):
    user_id = request.session.get('user_id')
    role = request.session.get('role')

    if not user_id or role != 'customer':
        return redirect('login')

    try:
        customer = Customer.objects.get(user_id=user_id)
    except Customer.DoesNotExist:
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
            # Lấy thông tin từ form
            city = request.POST.get('city')
            district = request.POST.get('district')
            ward = request.POST.get('ward')
            street = request.POST.get('street')

            # Tạo địa chỉ mới
            address = Address.objects.create(
                customer=customer,
                city=city,
                district=district,
                ward=ward,
                street=street,
            )

        order = Order.objects.create(
            customer=customer,
            address=address,
            total_amount=0,
            shipping_fee=Decimal('0'),
            status='pending',
            payment_status='unpaid',
            payment_method=payment_method,
        )

        total = Decimal('0')
        for product_id, item in cart.items():
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                continue

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

        request.session.pop('cart', None)
        request.session.modified = True

        return render(request, 'order_success.html', {'order': order})

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

    addresses = Address.objects.filter(customer=customer)
    user_info = customer.user

    return render(request, 'checkout.html', {
        'selected_items': selected_items,
        'total': total,
        'addresses': addresses,
        'user_name': user_info.name,
        'user_phone': user_info.telephone,
    })

'''

from collections import defaultdict
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404


def checkout(request):
    user_id = request.session.get('user_id')
    role = request.session.get('role')

    if not user_id or role != 'customer':
        return redirect('login')

    try:
        customer = Customer.objects.get(user_id=user_id)
    except Customer.DoesNotExist:
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
                customer=customer,
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
                customer=customer,
                seller=seller,  # đảm bảo model Order có field này
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

    addresses = Address.objects.filter(customer=customer)
    user_info = customer.user

    return render(request, 'checkout.html', {
        'selected_items': selected_items,
        'total': total,
        'addresses': addresses,
        'user_name': user_info.name,
        'user_phone': user_info.telephone,
    })




def manage_orders(request):
    status = request.GET.get('status')
    orders = Order.objects.all()
    if status:
        orders = orders.filter(status=status)

    return render(request, 'orders/manage_orders.html', {
        'orders': orders,
        'status': status
    })
    


'''def order_history(request):
    user_id = request.session.get('user_id')
    role = request.session.get('role')

    # Kiểm tra đăng nhập
    if not user_id or role != 'customer':
        return redirect('login')  # Không phải customer thì không được xem

    try:
        # Tìm customer có liên kết với user_id này
        customer = Customer.objects.get(user_id=user_id)
        print(f"[DEBUG] Đăng nhập với user_id={user_id}, tương ứng customer_id={customer.id}")
    except Customer.DoesNotExist:
        return render(request, 'error.html', {'message': 'Không tìm thấy thông tin khách hàng!'})
    # Lọc đơn hàng theo khách hàng này
    orders = Order.objects.filter(customer=customer).order_by('-created_at')

    context = {
        'pending_orders': orders.filter(status='pending'),
        'shipping_orders': orders.filter(status='shipping'),
        'delivered_orders': orders.filter(status='delivered'),
        'cancelled_orders': orders.filter(status='cancelled'),
        'customer': customer,
    }

    return render(request, 'order_history.html', context)
    '''


def order_history(request):
    user_id = request.session.get('user_id')
    role = request.session.get('role')

    if not user_id or not role:
        return redirect('login')

    if role == 'customer':
        # Xử lý lịch sử đơn hàng của khách hàng
        try:
            customer = Customer.objects.get(user_id=user_id)
        except Customer.DoesNotExist:
            return render(request, 'error.html', {'message': 'Không tìm thấy khách hàng!'})

        orders = Order.objects.filter(customer=customer).order_by('-created_at')

        context = {
            'pending_orders': orders.filter(status='pending'),
            'shipping_orders': orders.filter(status='shipping'),
            'delivered_orders': orders.filter(status='delivered'),
            'cancelled_orders': orders.filter(status='cancelled'),
            'role': role,
        }
        return render(request, 'order_history.html', context)

    elif role == 'seller':
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
    

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@require_POST
def approve_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'shipping'
    order.save()
    messages.success(request, f"Đã phê duyệt đơn hàng #{order.id}.")
    return redirect('order_history')

@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'cancelled'
    order.save()
    messages.warning(request, f"Đã huỷ đơn hàng #{order.id}.")
    return redirect('order_history')

@require_POST
def mark_delivered(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'delivered'
    order.save()
    messages.success(request, f"Đã giao đơn hàng #{order.id}.")
    return redirect('order_history')
