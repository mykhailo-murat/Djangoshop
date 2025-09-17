from django.shortcuts import render, redirect, get_object_or_404
from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart


# Create your views here.


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST, request=request)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                )
            cart.clear()
            return redirect('orders:order_created', order_id=order.id)
    else:
        form = OrderCreateForm(request=request)

    return render(request, 'order/create.html', {'cart': cart, 'form': form})


def order_created(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'order/created.html', {'order': order})
