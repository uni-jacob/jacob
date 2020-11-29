import os
import random

import hyperjson
from loguru import logger
from vkwave.api import API
from vkwave.bots import DefaultRouter
from vkwave.bots import MessageFromConversationTypeFilter
from vkwave.bots import SimpleBotEvent
from vkwave.bots import simple_bot_message_handler
from vkwave.bots import SimpleLongPollBot
from vkwave.bots import TextFilter
from vkwave.client import AIOHTTPClient

from database import utils as db
from database.models import Chat
from database.models import Student
from services import call
from services import filters
from services import keyboard as kbs
from services import media
from services.exceptions import EmptyCallMessage
from services.exceptions import StudentNotFound
from services.filters import PLFilter
from services.logger.config import config

main_router = DefaultRouter()
api_session = API(tokens=os.getenv("VK_CANARY_TOKEN"), clients=AIOHTTPClient())
api = api_session.get_context()
logger.configure(**config)


@simple_bot_message_handler(
    main_router,
    TextFilter(["старт", "начать", "start", "привет", "hi", "hello"])
    | PLFilter({"button": "main_menu"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _greeting(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        try:
            student_id = db.students.get_system_id_of_student(
                ans.object.object.message.peer_id,
            )
        except StudentNotFound:
            await ans.answer(
                """Вы не являетесь зарегистрированным студентом.
                Желаете попасть в существующую группу или создать свою?""",
                keyboard=kbs.main.choose_register_way(),
            )
        else:
            await ans.answer(
                "Привет!",
                keyboard=kbs.main.main_menu(
                    student_id,
                ),
            )


@simple_bot_message_handler(
    main_router,
    PLFilter({"button": "create_new_group"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _show_universities(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        # режим: выбор универа
        await ans.answer(
            "Выбери университет",
            keyboard=kbs.main.universities(),
        )
