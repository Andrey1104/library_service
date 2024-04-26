from django.urls import include, path
from rest_framework import routers

from library.views import BookViewSet, BorrowingViewSet

router = routers.DefaultRouter()
router.register(r"books", BookViewSet)
router.register(r"borrowings", BorrowingViewSet)

urlpatterns = [
    path("", include(router.urls))
]

app_name = "library"
