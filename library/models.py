from datetime import date, timedelta

from django.db import models
from rest_framework.exceptions import ValidationError

from library_service.settings import AUTH_USER_MODEL


class Book(models.Model):
    COVERS = [
        ("HARD", "hardcover"),
        ("SOFT", "softcover")
    ]
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=9, choices=COVERS)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=4, decimal_places=2)

    class Meta:
        ordering = ["title", "author"]
        verbose_name_plural = "books"

    def __str__(self):
        return self.title


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)

    def clean(self):
        if not self.borrow_date:
            self.borrow_date = date.today()
        if self.borrow_date >= self.expected_return_date:
            raise ValidationError("Expected return date must be after borrow date")
        if self.actual_return_date and self.actual_return_date < self.borrow_date:
            raise ValidationError("Actual return date must be after borrow date")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def overdue_days(self) -> int:
        return (self.actual_return_date - self.expected_return_date).days - 1

    @property
    def borrow_days(self) -> int:
        return (self.expected_return_date - self.borrow_date).days
    
    @property
    def expiated(self) -> bool:
        if not self.actual_return_date:
            self.actual_return_date = date.today()
        return self.expected_return_date < self.actual_return_date
