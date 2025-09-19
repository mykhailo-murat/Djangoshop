from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal, ROUND_HALF_UP
from orders.models import Order
from django.conf import settings
import stripe
from django.urls import reverse
import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect, HttpResponse

# Create your views here.


stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


def to_cents(d: Decimal) -> int:
    return int((d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) * 100).to_integral_value())


def payment_process(request):
    order_id = request.session.get('order_id', None)
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        success_url = request.build_absolute_uri(
            reverse('payment:completed')
        )
        cancel_url = request.build_absolute_uri(
            reverse('payment:canceled')
        )
        session_data = {
            'mode': 'payment',
            'client_reference_id': str(order.id),
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': [],
            'payment_intent_data': {
                'metadata': {'order_id': str(order.id)},
            },
        }

        for item in order.items.all():
            discounted_price = item.product.sell_price()
        session_data['line_items'].append({
            'price_data': {
                'unit_amount': int(discounted_price * Decimal('100')),
                'currency': 'usd',
                'product_data': {
                    'name': item.product.name,
                },
            },
            'quantity': item.quantity,
        })
        session = stripe.checkout.Session.create(**session_data)
        logger = logging.getLogger("stripe")
        logger.info("Created session %s for order %s", session.id, order.id)

        return redirect(session.url, code=303)
    else:
        return render(request, 'payment/process.html', locals())


def payment_completed(request):
    return render(request, 'payment/completed.html')


def payment_canceled(request):
    return render(request, 'payment/canceled.html')


@csrf_exempt
def test_webhook(request):
    print("🔥 Test webhook received", request.method)
    return HttpResponse("OK")
