import stripe

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from library_service.settings import STRIPE_SECRET_KEY
from payment.models import Payment
from payment.serializers import PaymentSerializer, PaymentDetailSerializer

stripe.api_key = STRIPE_SECRET_KEY


class PaymentViewSet(ListAPIView, RetrieveAPIView, GenericViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Payment.objects.all()
        return Payment.objects.filter(borrowing_id=user.pk)

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentSerializer

        return self.serializer_class


def create_stripe_session(payment: Payment):
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(payment.money_to_pay * 100),
                    "product_data": {
                        "name": payment.borrowing.book.title,
                    },
                },
                "quantity": 1,
            }
        ],
        metadata={"book_id": payment.borrowing.book.id},
        mode="payment",
        success_url='http://localhost:8800/api/payment',
        cancel_url='http://localhost:8800/api/',
        customer_email=payment.borrowing.user.email
    )

    payment.session_url = checkout_session.url
    payment.session_id = checkout_session.id
    payment.save()

    return payment
