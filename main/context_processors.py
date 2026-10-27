from decimal import Decimal

from .models import ServiceItem


def cart_total(request):
    """Expose the current cart total in the site header."""
    cart = request.session.get('cart', {})
    quantities = {}

    if isinstance(cart, dict):
        for item_id, quantity in cart.items():
            try:
                item_id = int(item_id)
                quantity = int(quantity)
            except (TypeError, ValueError):
                continue
            if item_id > 0 and quantity > 0:
                quantities[item_id] = quantity

    total = Decimal('0.00')
    for item in ServiceItem.objects.filter(id__in=quantities):
        total += item.price * quantities[item.id]

    return {'cart_total': total}
