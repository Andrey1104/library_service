from django.db import models


class Book(models.Model):
    COVERS = [
        ("HARD", "hardcover"),
        ("SOFT", "softcover")
    ]
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=9, choices=COVERS)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(decimal_places=2)

    class Meta:
        ordering = ["title", "author"]
        verbose_name_plural = "books"

    def __str__(self):
        return self.title
