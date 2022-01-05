import asyncio
import logging
import os
from logging.handlers import SysLogHandler

import sentry_sdk
from loguru import logger
from vkbottle import Bot, OrFilter, load_blueprints_from_package
from vkbottle.bot import Message

from jacob.config import get_token
from jacob.database.utils.admins import is_admin
from jacob.database.utils.init import init_db_connection
from jacob.database.utils.students import is_student
from jacob.database.utils.users import create_user, get_user_id, set_state
from jacob.services import keyboards as kb
from jacob.services.api import send_empty_keyboard
from jacob.services.common import vbml_rule
from jacob.services.middleware import ChangeSentryUser
from jacob.services.rules import EventPayloadContainsRule

handler = SysLogHandler(address=(os.getenv("LOG_HOST"), int(os.getenv("LOG_PORT"))))
logger.add(handler)

bot = Bot(token=get_token())
bot.labeler.vbml_ignore_case = True
bot.labeler.message_view.register_middleware(ChangeSentryUser())
vbml_rule = vbml_rule(bot)

sentry_sdk.init(
    os.getenv("SENTRY_URL"),
    environment=os.getenv("ENV"),
    traces_sample_rate=1.0,
)

for bp in load_blueprints_from_package("jacob/blueprints"):
    bp.load(bot)


@bot.on.message(
    OrFilter(
        vbml_rule(["привет", "начать", "hello", "hi"]),
        EventPayloadContainsRule({"block": "main_menu"}),
    ),
)
async def greeting(message: Message):
    logging.info("Приветствие пользователя")
    await message.answer("Привет!")
    if not await is_student(message.peer_id):
        logging.info("Пользователь здесь впервые, создание анонимного профиля")
        await create_user(message.peer_id)
        await set_state(message.peer_id, "main")
        await send_empty_keyboard(message)
        await message.answer(
            "Вы не являетесь пользователем. Создайте новую группу.",
            keyboard=kb.register_start(),
        )
    else:
        logging.info("Пользователь здесь уже был. Отправка клавиатуры главного меню")
        user_id = await get_user_id(message.peer_id)
        await message.answer(
            "Добро пожаловать!",
            keyboard=kb.main_menu(await is_admin(user_id)),
        )


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init_db_connection())
    bot.run_forever()
