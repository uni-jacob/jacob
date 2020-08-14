from vkwave.bots import DefaultRouter
from vkwave.bots import SimpleBotEvent
from vkwave.bots import simple_bot_message_handler

from services import filters

preferences_router = DefaultRouter()


@simple_bot_message_handler(
    preferences_router, filters.PLFilter({"button": "settings"})
)
async def open_preferences(ans: SimpleBotEvent):
    await ans.answer("тут будут настройки")
