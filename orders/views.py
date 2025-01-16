from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from products.models import Product
from django.db.models import Sum, Count
from .serializers import OrderSerializer
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema

User = get_user_model()


class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=OrderSerializer)
    def post(self, request):
        data = request.data
        items = data.pop("items", [])
        total_price = 0
        serializer = OrderSerializer(data=data)

        for item in items:
            product = Product.objects.filter(pk=item["product"]).first()
            if not product:
                return Response(
                    {
                        "error": f"Product with id {item['product']} \
                                not found."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            total_price += item["quantity"] * product.price

        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            order = serializer.save(user=request.user)
            order_items = [
                OrderItem(
                    order=order,
                    product_id=item["product"],
                    quantity=item["quantity"],
                    price=item["price"],
                )
                for item in items
            ]
            OrderItem.objects.bulk_create(order_items)
            return Response(OrderSerializer(order).data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: OrderSerializer(many=True)})
    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=OrderSerializer)
    def put(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user)

        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={204: "No Content"})
    def delete(self, request, pk):
        try:
            order = Order.objects.get(
                pk=pk, user=request.user, status="PENDING")
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found or cannot be deleted"},
                status=status.HTTP_404_NOT_FOUND,
            )
        order.delete()
        return Response(
            {"error": "Order deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


class AdminOrderUpdateView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(request_body=OrderSerializer)
    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )

        status_value = request.data.get("status")
        if status_value not in ["PENDING", "COMPLETED", "CANCELLED"]:
            return Response(
                {"error": "Invalid status value."},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = status_value
        order.save()
        return Response(
            {"message": f"Order status to {status_value}."},
            status=status.HTTP_200_OK
        )


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: OrderSerializer(many=True)})
    def get(self, request):
        user = request.user

        if user.is_staff:
            orders = Order.objects.all()
        else:
            orders = Order.objects.filter(user=user)
        status_filter = request.query_params.get("status")
        if status_filter:
            orders = orders.filter(status=status_filter)

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class AdminStatisticsView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(responses={200: OrderSerializer(many=True)})
    def get(self, request):
        total_orders = Order.objects.count()
        order_by_status = Order.objects.values(
            "status").annotate(count=Count("id"))
        total_users = User.objects.count()
        top_products = Product.objects.annotate(
            total_sold=Sum("orderitem_quantity")
        ).order_by("-total_sold")[:5]

        data = {
            "total_orders": total_orders,
            "order_by_status": order_by_status,
            "total_users": total_users,
            "top_products": [
                {"name": p.name,
                 "total_sold": p.total_sold} for p in top_products
            ],
        }

        return Response(data)


class UserStatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: OrderSerializer(many=True)})
    def get(self, request):
        user = request.user
        user_orders = Order.objects.filter(user=user)
        total_spent = user_orders.aggregate(Sum("total_price"))[
            "total_price_sum"] or 0
        order_by_status = user_orders.values(
            "status").annotate(count=Count("id"))

        data = {
            "total_orders": user_orders.count(),
            "order_by_status": order_by_status,
            "total_spent": total_spent,
        }

        return Response(data)


class TimeRangeStatisticsView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(responses={200: OrderSerializer(many=True)})
    def get(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if not start_date or not end_date:
            return Response(
                {"error": "Please provide 'start_date' and \
                    'end_date' parameters"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(
                end_date, "%Y-%m-%d") + timedelta(days=1)

        except ValueError:
            return Response(
                {"error": "Invalid date format. Use 'YYYY-MM-DD'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        orders = Order.objects.filter(created_at__range=(start_date, end_date))
        total_orders = orders.count()
        total_revenue = orders.aggregate(Sum("total_price"))[
            "total_price__sum"] or 0

        date = {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "date_range": f"{start_date.date()} or {end_date.date()}",
        }

        return Response(date)
