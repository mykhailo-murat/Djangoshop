import stripe
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from orders.models import Order
from main.models import Product
import logging

logger = logging.getLogger("stripe")


@csrf_exempt
def stripe_webhook(request):
    logger.info("🔔 Webhook received!")

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        logger.warning("⚠️ Webhook verification failed: %s", e)
        return HttpResponse(status=400)

    event_type = event['type']
    data = event['data']['object']

    logger.info("✅ Stripe event type: %s", event_type)

    if event_type == 'checkout.session.completed':
        logger.info("🎯 Handling 'checkout.session.completed'")

        if data.get('mode') == 'payment' and data.get('payment_status') == 'paid':
            order_id = data.get('client_reference_id')
            payment_intent = data.get('payment_intent')

            logger.info("🔍 Order ID from session: %s", order_id)

            if order_id:
                updated = Order.objects.filter(pk=order_id).update(
                    paid=True,
                    stripe_id=payment_intent
                )
                logger.info("✅ Order #%s marked as paid (updated: %s)", order_id, updated)
            else:
                logger.warning("❌ Order ID not found in session data")

    elif event_type == 'payment_intent.succeeded':
        logger.info("🎯 Handling 'payment_intent.succeeded'")

        metadata = data.get('metadata', {})
        order_id = metadata.get('order_id')

        logger.info("🔍 Order ID from intent: %s", order_id)

        if order_id:
            updated = Order.objects.filter(pk=order_id).update(
                paid=True,
                stripe_id=data.get('id')
            )
            logger.info("✅ Order #%s marked as paid (updated: %s)", order_id, updated)
        else:
            logger.warning("❌ Order ID not found in intent metadata")

    else:
        logger.info("ℹ️ Unhandled event type: %s", event_type)

    return HttpResponse(status=200)
