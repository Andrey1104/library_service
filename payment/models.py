from django.db import models

from library.models import Borrowing


class Payment(models.Model):
    status = models.CharField(max_length=10, choices=[('PENDING', 'Pending'), ('PAID', 'Paid')])
    type = models.CharField(max_length=10, choices=[('PAYMENT', 'Payment'), ('FINE', 'Fine')])
    borrowing = models.OneToOneField(Borrowing, on_delete=models.CASCADE)
    session_url = models.URLField()
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
