"""Блок Студенты."""

from loguru import logger
from vkwave import bots

from jacob.services import filters
from jacob.services import keyboard as kbs
from jacob.services.logger import config as logger_config

group_router = bots.DefaultRouter()
logger.configure(**logger_config.config)


@bots.simple_bot_message_handler(
    group_router,
    filters.PLFilter({"button": "group_mgmt"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _start_group(ans: bots.SimpleBotEvent):
    await ans.answer(
        "Меню группы",
        keyboard=kbs.group.group_menu(),
    )
