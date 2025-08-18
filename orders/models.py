from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from decimal import Decimal

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    # Store values directly in DB
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.id}"

    def calculate_totals(self):
        """
        Recalculate subtotal, tax, and total from items.
        Useful if prices or quantities change after creation.
        """
        self.subtotal = sum(item.get_cost() for item in self.items.all())
        self.tax_amount = self.subtotal * Decimal('0.18')  # 18% GST
        self.total = self.subtotal + self.tax_amount
        return self.total


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


    def get_cost(self):
        return self.price * self.quantity  # ✅ use stored price, not product.price
