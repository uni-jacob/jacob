import logging
import os

from loguru import logger
from vkwave.bots import MessageFromConversationTypeFilter
from vkwave.bots import SimpleBotEvent
from vkwave.bots import SimpleLongPollBot
from vkwave.bots import TextFilter

from blueprints.main import main
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
from services.filters import PLFilter
from services.logger.config import config

__version__ = "2.15.0"

from services.logger.handlers import InterceptHandler

bot = SimpleLongPollBot(
    tokens=os.getenv("VK_TOKEN"),
    group_id=os.getenv("GROUP_ID"),
)
bot.dispatcher.add_router(main.main_router)
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


bot.run_forever()
