from datetime import date

from django.shortcuts import redirect
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from library.models import Book, Borrowing
from library.serializers import BookSerializer, BorrowingSerializer, BorrowingListSerializer
from library_service.settings import FINE_COEFFICIENT
from payment.models import Payment
from payment.views import create_stripe_session
from utils.telegram_bot import send_message


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BorrowingViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet
):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]

    @staticmethod
    def str_to_int(char: str):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in char.split(",") if str_id]

    def get_queryset(self):
        queryset = self.queryset
        user_id = self.request.query_params.get("user_id")

        if not self.request.user.is_superuser:
            return queryset.filter(user=self.request.user)

        if user_id:
            user_id = self.str_to_int(user_id)
            queryset = queryset.filter(user__id__in=user_id)

        return queryset

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return BorrowingListSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        book = Book.objects.get(id=request.data.get("book"))
        user = self.request.user
        return_date = request.data.get("expected_return_date")

        text = (
            f"You have new borrowing \n"
            f"Took \"{book}\" book.\n"
            f"Expected return on {return_date}.\n"
            f"Daily fee: {book.daily_fee} $"
        )
        send_message(chat_id=user.telegram_id, message=text)

        return super().create(request, *args, **kwargs)

    @staticmethod
    def calculate_payable(borrowing, request):
        payment_type = "PAYMENT"
        payable = (date.today() - borrowing.borrow_date).days * borrowing.book.daily_fee
        if borrowing.expiated:
            payment_type = "FINE"
            payable = (
                (borrowing.overdue_days + borrowing.borrow_days)
                * borrowing.book.daily_fee
            ) * FINE_COEFFICIENT

        payment = Payment.objects.create(
            status="PENDING",
            type=payment_type,
            borrowing_id=borrowing.id,
            session_url=request.build_absolute_uri(),
            session_id=request.session.session_key,
            money_to_pay=payable
        )
        # payment.save()
        # create_stripe_session(payment)

        return payment

    @action(
        methods=["POST"],
        detail=True,
        url_path="return",
        permission_classes=[IsAuthenticated]
    )
    def return_borrowing(self, request, pk=None):
        borrowing = get_object_or_404(Borrowing, pk=pk)

        # if borrowing.actual_return_date:
        #     return Response(status=status.HTTP_400_BAD_REQUEST)
        #
        # borrowing.actual_return_date = date.today()
        # borrowing.book.inventory += 1

        payment = self.calculate_payable(borrowing, request)

        # borrowing.save()
        # borrowing.book.save()

        # return Response(status=status.HTTP_204_NO_CONTENT)
        return create_stripe_session(payment)
        # return redirect(url, status=status.HTTP_307_TEMPORARY_REDIRECT)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "user_id",
                type={"type": "list", "items": {"type": "number"}},
                description=(
                        "Admin user ids filter "
                        "for borrowings (eg. ?user_id=1,3)")
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
