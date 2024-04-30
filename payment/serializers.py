from rest_framework import serializers

from library.serializers import BorrowingListSerializer
from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "money_to_pay"
        )


class PaymentDetailSerializer(serializers.ModelSerializer):
    borrowing = BorrowingListSerializer()

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "session_url",
            "session_id",
            "money_to_pay",
            "borrowing"
        )
