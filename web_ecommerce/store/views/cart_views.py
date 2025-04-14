from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Cart, CartItem
from django.contrib.auth.decorators import login_required





'''def cart_detail(request):
    if 'user_id' not in request.session:
        return redirect('/login/?next=/cart/')

    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
    cart, _ = Cart.objects.get_or_create(user=user)
    items = CartItem.objects.filter(cart=cart)
    total = sum(item.subtotal() for item in items)

    return render(request, 'cart.html', {'items': items, 'total': total})'''


# views.py

from django.shortcuts import render, redirect, get_object_or_404
from store.models import Cart, CartItem, Product, User

'''def cart_detail(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/login/?next=/cart/')

    user = get_object_or_404(User, id=user_id)
    cart, _ = Cart.objects.get_or_create(user=user)

    items = cart.items.all()
    total = sum(item.subtotal() for item in items)

    return render(request, 'cart.html', {'items': items, 'total': total})'''
    
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



'''def remove_from_cart(request, item_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/login/?next=/cart/')

    item = get_object_or_404(CartItem, id=item_id)
    item.delete()

    return redirect('/cart/')'''
    
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]

    # Nếu cart rỗng sau khi xóa -> xóa luôn khỏi session
    if not cart:
        request.session.pop('cart', None)
    else:
        request.session['cart'] = cart

    request.session.modified = True
    return redirect('cart_detail')

from django.views.decorators.http import require_POST

'''
    
def update_cart(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})

        action = request.POST.get('action')
        if action:
            if action.startswith('remove-'):
                product_id = action.split('-')[1]
                if product_id in cart:
                    del cart[product_id]

        # Cập nhật lại session
        if not cart:
            request.session.pop('cart', None)
        else:
            request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart_detail')
'''

def update_cart(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        action = request.POST.get('action')

        if action:
            action_type, product_id = action.split('-')
            product_id = str(product_id)

            if action_type == 'increase':
                if product_id in cart:
                    cart[product_id]['quantity'] += 1

            elif action_type == 'decrease':
                if product_id in cart:
                    if cart[product_id]['quantity'] > 1:
                        cart[product_id]['quantity'] -= 1
                    else:
                        # Nếu còn 1, giảm nữa thì xóa luôn
                        del cart[product_id]

            elif action_type == 'remove':
                if product_id in cart:
                    del cart[product_id]

        # Cập nhật lại session
        if cart:
            request.session['cart'] = cart
        else:
            request.session.pop('cart', None)

        request.session.modified = True

    return redirect('cart_detail')
