import stripe
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.decorators import action

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

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

    @action(detail=False, methods=['get'], url_path="status",)
    def check_payment_status(self, request):
        """
        Task to create a post.
        """
        payments = Payment.objects.filter(status="PENDING")
        if payments:
            for payment in payments:
                payment_session = stripe.checkout.Session.retrieve(
                    id=payment.session_id
                )
                status1 = payment_session.payment_status
                print(status1)
        return Response(status=status.HTTP_200_OK)


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
        success_url='http://localhost:8800/api/payments',
        cancel_url='http://localhost:8800/api/',
        customer_email=payment.borrowing.user.email
    )

    payment.session_url = checkout_session.url
    payment.session_id = checkout_session.id
    payment.save()

    return redirect(checkout_session.url, status=status.HTTP_307_TEMPORARY_REDIRECT)
