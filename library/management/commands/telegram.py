import asyncio

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from django.core.management.base import BaseCommand

from library_service.settings import TOKEN
from utils.telegram_bot import dp


class Command(BaseCommand):

    def handle(self, *args, **options):
        bot = Bot(
            token=TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        print("Bot started")
        asyncio.run(dp.start_polling(bot))
