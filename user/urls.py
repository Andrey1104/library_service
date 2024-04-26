from django.urls import path

from user.views import ManageUserView, CreateUserView

urlpatterns = [
    path("me/", ManageUserView.as_view(), name="manage"),
    path("register/", CreateUserView.as_view(), name="register")
]

app_name = "user"
