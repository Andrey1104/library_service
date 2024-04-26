from django.db import models
from django.db.models import Count, F, ExpressionWrapper, IntegerField, Q

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

    def free(self):
        available_books_count = (
            Book.objects.annotate(
                borrowed_count=Count(
                    "borrowing",
                    filter=~Q(borrowing__actual_return_date__isnull=True)
                )
            )
            .annotate(
                available_inventory=ExpressionWrapper(
                    F("inventory") - F("borrowed_count"),
                    output_field=IntegerField()
                )
            )
            .values_list("title", "available_inventory")
        )
        return available_books_count.filter(
            title=self.title,
            author=self.author
        ).values_list("available_inventory", flat=True).first()


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(auto_now=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
