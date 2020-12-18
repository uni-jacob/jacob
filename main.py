import logging
import os

from loguru import logger
from vkwave.bots import MessageFromConversationTypeFilter
from vkwave.bots import SimpleBotEvent
from vkwave.bots import SimpleLongPollBot
from vkwave.bots import TextFilter

from blueprints import call
from blueprints import chats
from blueprints import contacts
from blueprints import finances
from blueprints import preferences
from blueprints import report
from blueprints import schedule
from blueprints import web
from database import utils as db
from services import keyboard as kbs
from services.exceptions import StudentNotFound
from services.filters import PLFilter
from services.logger.config import config

__version__ = "2.15.2"

from services.logger.handlers import InterceptHandler

bot = SimpleLongPollBot(
    tokens=os.getenv("VK_TOKEN"),
    group_id=os.getenv("GROUP_ID"),
)
bot.dispatcher.add_router(call.call_router)
bot.dispatcher.add_router(preferences.preferences_router)
bot.dispatcher.add_router(chats.chats_router)
bot.dispatcher.add_router(finances.finances_router)
bot.dispatcher.add_router(schedule.schedule_router)
bot.dispatcher.add_router(web.web_router)
bot.dispatcher.add_router(report.report_router)
bot.dispatcher.add_router(contacts.contacts_router)

logger.configure(**config)
logging.basicConfig(level=logging.DEBUG, handlers=[InterceptHandler()])


@bot.message_handler(
    TextFilter(["старт", "начать", "start", "привет", "hi", "hello"])
    | PLFilter({"button": "main_menu"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def start(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        try:
            student_id = (
                db.students.get_system_id_of_student(
                    ans.object.object.message.peer_id,
                ),
            )
        except StudentNotFound:
            await ans.answer(
                """Вы не являетесь зарегестрированным студентом.
                Чтобы получить доступ, напишите @dadyarri университет, названия группы и направления"""
            )
        else:
            await ans.answer(
                "Привет!",
                keyboard=kbs.main.main_menu(student_id),
            )


bot.run_forever()
