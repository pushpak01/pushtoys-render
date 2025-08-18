from decimal import Decimal, InvalidOperation
from django.conf import settings
from products.models import Product



class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    # Default Indian GST rates if not in settings
    if not hasattr(settings, 'INDIAN_TAX_RATES'):
        settings.INDIAN_TAX_RATES = {
            'GST': {
                'cgst': Decimal('0.09'),  # 9%
                'sgst': Decimal('0.09'),  # 9%
                'igst': Decimal('0.18'),  # 18%
            }
        }


    def add(self, product, quantity=1, override_quantity=False):
            product_id = str(product.id)
            price_str = str(product.price)  # <-- store string, not Decimal
            if product_id in self.cart:
                if override_quantity:
                    self.cart[product_id]['quantity'] = quantity
                else:
                    self.cart[product_id]['quantity'] += quantity
            else:
                self.cart[product_id] = {
                    'quantity': quantity,
                    'price': price_str,  # saved as string
                    'product_id': product_id,
                }
            self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        self.session['cart'] = {}
        self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        product_map = {str(p.id): p for p in products}
        for pid, item in list(self.cart.items()):
            # convert back to Decimal for arithmetic and attach product object
            item['product'] = product_map.get(pid)
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_subtotal(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())


    def get_total_price(self):
        """
        Get total price without tax (used in template easily).
        """
        return self.get_subtotal()

    def calculate_taxes(self, state_code=None):
        """
        Calculate Indian GST taxes with state-specific logic.
        Returns: dict of tax breakdown.
        """
        subtotal = self.get_subtotal()
        taxes = {
            'cgst': Decimal('0'),
            'sgst': Decimal('0'),
            'igst': Decimal('0'),
            'total_tax': Decimal('0')
        }

        if state_code:  # Inter-state (IGST)
            taxes['igst'] = subtotal * settings.INDIAN_TAX_RATES['GST']['igst']
        else:  # Intra-state (CGST + SGST)
            taxes['cgst'] = subtotal * settings.INDIAN_TAX_RATES['GST']['cgst']
            taxes['sgst'] = subtotal * settings.INDIAN_TAX_RATES['GST']['sgst']

        taxes['total_tax'] = taxes['igst'] if state_code else (taxes['cgst'] + taxes['sgst'])
        return taxes

    def get_grand_total(self, state_code=None):
        """
        Get complete order breakdown including taxes.
        """
        subtotal = self.get_subtotal()
        taxes = self.calculate_taxes(state_code)
        return {
            'subtotal': subtotal,
            'taxes': taxes,
            'grand_total': subtotal + taxes['total_tax']
        }

    def get_product(self, product_id):
        """Get product details from cart"""
        return self.cart.get(str(product_id))

    def validate_cart(self):
        """Validate all cart items are available"""
        for item_id, item in self.cart.items():
            try:
                product = Product.objects.get(id=item_id)
                if product.price != Decimal(item['price']):
                    item['price'] = str(product.price)
            except (Product.DoesNotExist, InvalidOperation):
                self.remove(item_id)
        self.save()
