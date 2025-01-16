from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Payment
from orders.models import Order
from .serializers import PaymentSerializer
from drf_yasg.utils import swagger_auto_schema


class MockPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        response_body=PaymentSerializer,
        responses={200: PaymentSerializer(many=True)})
    def post(self, request):
        order_id = request.data.get("order_id")
        order = Order.objects.filter(id=order_id, user=request.user).first()
        if not order:
            return Response({"error": "Order not found or unaythorized."},
                            status=status.HTTP_404_NOT_FOUND)

        payment_status = "Paid" if request.data.get(
            "success", True) else "Failed"

        payment, created = Payment.objects.get_or_create(order=order)
        payment.amount = order.total_price
        payment.status = payment_status
        payment.save()

        return Response(
            {"message": f"Payment {payment_status.lower()} \
             for Order #{order_id}"},
            status=status.HTTP_200_OK
        )
