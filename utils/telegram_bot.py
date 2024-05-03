import asyncio

from aiogram import Dispatcher, html, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.deep_linking import decode_payload
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message
from asgiref.sync import sync_to_async

from library_service.settings import TOKEN
from user.models import User

dp = Dispatcher()


@sync_to_async
def set_user_telegram_id(user_id, telegram_id):
    user = User.objects.get(id=user_id)
    if not user.telegram_id:
        try:
            user.telegram_id = telegram_id
            user.save()
            return user.telegram_id
        except Exception as error:
            print(error)


@dp.message(CommandStart(deep_link=True))
async def handler(message: Message, command: CommandObject):
    args = command.args
    payload = decode_payload(args)
    telegram_id = await set_user_telegram_id(int(payload), int(message.chat.id))
    if telegram_id:
        await message.answer(
            f"Hello, {html.bold(message.from_user.full_name)}! "
            f"I will send to you a message about events "
            f"in our library. See you later..."
        )
    else:
        await message.answer("You don't have any notifications.")


def send_message(message: str, chat_id: int) -> None:
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    try:
        asyncio.run(bot.send_message(
            chat_id=chat_id,
            text=message
        ))
    except Exception as error:
        print(error)
