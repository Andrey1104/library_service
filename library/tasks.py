from datetime import datetime

import stripe
from celery import shared_task

from library.models import Borrowing
from payment.models import Payment
from user.models import User
from utils.telegram_bot import send_message


@shared_task
def overdue_notification():
    """Task to send notification about overdue borrowing at scheduled time"""
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lt=datetime.today(),
        actual_return_date__isnull=True
    )

    if overdue_borrowings:
        for borrowing in overdue_borrowings:
            text = (
                f"You have to return the book {borrowing.book}\n"
                f"you borrowed at {borrowing.borrow_date}"
            )
            send_message(message=text, chat_id=borrowing.user.telegram_id)


@shared_task
def check_payment_status():
    """
    Task to create a post.
    """
    payments = Payment.objects.filter(status="PENDING")
    if payments:
        for payment in payments:
            payment_session = stripe.checkout.Session.retrieve(
                id=payment.session_id
            )
            status = payment_session.payment_status
            print(status)
