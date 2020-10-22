import os

from loguru import logger
from vkwave.api import API
from vkwave.bots import DefaultRouter
from vkwave.bots import MessageFromConversationTypeFilter
from vkwave.bots import SimpleBotEvent
from vkwave.bots import simple_bot_message_handler
from vkwave.client import AIOHTTPClient

from services import filters
from services.logger.config import config

web_router = DefaultRouter()
api_session = API(tokens=os.getenv("VK_TOKEN"), clients=AIOHTTPClient())
api = api_session.get_context()
logger.configure(**config)


@simple_bot_message_handler(
    web_router,
    filters.PLFilter({"button": "web"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def start_call(ans: SimpleBotEvent):
    await ans.answer("Этот раздел находится в разработке")
