from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView, TokenObtainPairView

from user.views import ManageUserView, CreateUserView, UserTelegramView

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("me/", ManageUserView.as_view(), name="manage"),
    path("telegram/", UserTelegramView.as_view(), name="telegram")
]

app_name = "user"
