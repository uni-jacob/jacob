import asyncio
import logging
import os

from vkbottle import Bot, load_blueprints_from_package, OrFilter
from vkbottle.bot import Message
from vkbottle.dispatch.rules.bot import VBMLRule
import sentry_sdk

from jacob.database.utils.admins import is_admin
from jacob.database.utils.init import init_db_connection
from jacob.database.utils.students import is_student
from jacob.database.utils.users import create_user, set_state, get_user_id
from jacob.services import keyboards as kb
from jacob.services.api import send_empty_keyboard
from jacob.services.common import get_token
from jacob.services.middleware import ChangeSentryUser
from jacob.services.rules import EventPayloadContainsRule

logging.basicConfig(level="DEBUG")

bot = Bot(token=get_token())
bot.labeler.vbml_ignore_case = True
bot.labeler.message_view.register_middleware(ChangeSentryUser())
vbml_rule = VBMLRule.with_config(
    bot.labeler.rule_config
)  # FIXME: temporary fix, bug in vkbottle

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
    )
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
            "Добро пожаловать!", keyboard=kb.main_menu(await is_admin(user_id))
        )


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init_db_connection())
    bot.run_forever()
