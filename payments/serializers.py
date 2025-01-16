from rest_framework import serializers
from orders.models import Order, OrderItem
from .models import Payment


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'status', 'total_price', 'items']
        read_only_fields = ['id', 'user', 'created_at', 'total_price']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item in items_data:
            OrderItem.objects.create(order=order, **item)
        return order


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'status', 'payment_date']
        read_only_fields = ['id', 'created_at']
