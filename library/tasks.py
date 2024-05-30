from datetime import datetime, date

import stripe
from celery import shared_task

from library.models import Borrowing
from payment.models import Payment
from utils.telegram_bot import send_message


@shared_task
def overdue_notification():
    """Task to send notification about overdue borrowing at scheduled time"""
    print("overdue notification is started!!!")
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lt=datetime.today(),
        actual_return_date__isnull=True
    )

    if overdue_borrowings:
        for borrowing in overdue_borrowings:
            text = (
                f"You have to return the book {borrowing.book}\n"
                f"You borrowed it on {borrowing.borrow_date.strftime('%Y-%m-%d')}"
            )
            chat_id = borrowing.user.telegram_id

            if chat_id:
                try:
                    send_message(message=text, chat_id=chat_id)
                except Exception as e:
                    print(f"Failed to send message to user {borrowing.user}")
                    print(e)
            else:
                print(f"User {borrowing.user} has no Telegram ID")
    else:
        print("No overdue borrowings found")


@shared_task
def check_payment_status():
    payments = Payment.objects.filter(status="PENDING")
    if payments:
        for payment in payments:
            payment_session = stripe.checkout.Session.retrieve(
                id=payment.session_id
            )
            payment_status = payment_session.payment_status
            if payment_status == "paid":
                payment.status = "PAID"
                payment.borrowing.actual_return_date = date.today()
                payment.save()
                text = (
                    f"Your payment for the book "
                    f"{payment.borrowing.book.title} "
                    f"has been received!"
                )
                send_message(message=text, chat_id=payment.borrowing.user.telegram_id)
