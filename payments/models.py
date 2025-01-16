from django.db import models
from orders.models import Order


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[(
        'Pending', 'Pending'), ('Paid', 'Paid'), ('Failed', 'Failed')])
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order #{self.order.id} - {self.status}"
