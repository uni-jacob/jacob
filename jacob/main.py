import logging
import os

from vkbottle import Bot, load_blueprints_from_package
from vkbottle.bot import Message

from jacob.database.utils.users import is_user

logging.basicConfig(level="DEBUG")

bot = Bot(token=os.getenv("VK_TOKEN"))
bot.labeler.vbml_ignore_case = True

for bp in load_blueprints_from_package("blueprints"):
    bp.load(bot)


@bot.on.message(text=["привет", "начать", "hello", "hi"])
async def greeting(message: Message):
    await message.answer("Привет!")

    if not is_user(message.peer_id):  # Собеседник не пользователь
        await message.answer(
            "Вы не являетесь пользователем. Создайте новую группу или введите код приглашения",
            keyboard=...,
        )


bot.run_forever()
