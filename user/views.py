import asyncio

from aiogram import Bot
from aiogram.utils.deep_linking import create_start_link
from django.shortcuts import redirect
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from library_service.settings import TOKEN
from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserTelegramView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bot = Bot(TOKEN)
        user_id = self.request.user.id
        link = asyncio.run(create_start_link(
            bot,
            str(user_id),
            encode=True)
        )
        return redirect(link)
