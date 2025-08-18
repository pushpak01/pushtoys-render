from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from decimal import Decimal
from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart


@login_required
def checkout(request):
    cart = Cart(request)

    if not cart:
        messages.warning(request, "Your cart is empty")
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.user = request.user

                # Calculate and store values directly
                subtotal = cart.get_subtotal()
                tax = subtotal * Decimal('0.18')
                total = subtotal + tax

                order.subtotal = subtotal
                order.tax_amount = tax
                order.total = total
                order.save()  # ✅ Save before adding items

                # Create order items
                for item in cart:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        price=item['price'],  # store cart price
                        quantity=item['quantity']
                    )

                cart.clear()

                messages.success(request, "Your order has been placed successfully!")
                return render(request, 'orders/placed.html', {
                    'order': order,
                    'order_items': order.items.all()
                })
    else:
        initial_data = {
            'full_name': request.user.get_full_name(),
            'email': request.user.email,
        }
        form = OrderCreateForm(initial=initial_data)

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'form': form,
        'subtotal': cart.get_subtotal(),
        'tax_amount': cart.get_subtotal() * Decimal('0.18'),
        'grand_total': cart.get_grand_total()
    })

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).select_related().prefetch_related('items').order_by('-created_at')



    for order in orders:
        order.subtotal = sum(
            item.price * item.quantity
            for item in order.items.all()
        )
        order.tax_amount = order.subtotal * Decimal('0.18')
        order.grand_total = order.subtotal + order.tax_amount
        order.item_count = order.items.count()

    return render(request, 'orders/history.html', {
        'orders': orders,
        'title': 'Order History'
    })
