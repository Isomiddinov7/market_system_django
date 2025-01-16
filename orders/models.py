from django.db import models
from products.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Kutilmoqda'),
        ('CONFIRMED', 'Tasdiqlangan'),
        ('DELIVERED', 'Yetkazib berildi'),
        ('CANCELLED', 'Bekor qilingan'),
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders")
    products = models.ManyToManyField(Product, through="OrderItem")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}\n" \
           f"in Order #{self.order.id}"
