import os

import hyperjson
from loguru import logger
from vkwave.api import API
from vkwave.bots import DefaultRouter
from vkwave.bots import SimpleBotEvent
from vkwave.bots import simple_bot_message_handler
from vkwave.client import AIOHTTPClient

from database import utils as db
from services import filters
from services import keyboard as kbs
from services.logger.config import config

finances_router = DefaultRouter()
api_session = API(tokens=os.getenv("VK_TOKEN"), clients=AIOHTTPClient())
api = api_session.get_context()
logger.configure(**config)


@simple_bot_message_handler(finances_router, filters.PLFilter({"button": "finances"}))
async def finances(ans: SimpleBotEvent):
    await ans.answer(
        "Список финансовых категорий",
        keyboard=kbs.finances.list_of_fin_categories(ans.object.object.message.from_id),
    )


@simple_bot_message_handler(
    finances_router, filters.PLFilter({"button": "fin_category"})
)
async def fin_category_menu(ans: SimpleBotEvent):
    payload = hyperjson.loads(ans.object.object.message.payload)
    category_object = db.finances.find_fin_category(id=payload["category"])
    await ans.answer(
        f'Меню категории "{category_object.name}"',
        keyboard=kbs.finances.fin_category(payload["category"]),
    )
