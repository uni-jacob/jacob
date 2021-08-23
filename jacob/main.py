import asyncio
import logging
import os

from vkbottle import Bot, load_blueprints_from_package
from vkbottle.bot import Message

from jacob.database.utils.init import init_db_connection
from jacob.database.utils.users import is_user
from jacob.services import keyboards as kb

logging.basicConfig(level="DEBUG")

bot = Bot(token=os.getenv("VK_TOKEN"))
bot.labeler.vbml_ignore_case = True

for bp in load_blueprints_from_package("jacob/blueprints"):
    bp.load(bot)


@bot.on.message(text=["привет", "начать", "hello", "hi"])
async def greeting(message: Message):
    await message.answer("Привет!")
    if not await is_user(message.peer_id):  # Собеседник не пользователь
        # TODO: Создать анонимного пользователя
        await message.answer(
            "Вы не являетесь пользователем. Создайте новую группу или введите код приглашения",
            keyboard=kb.main_menu.register_or_invite(),
        )


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init_db_connection())
    bot.run_forever()
