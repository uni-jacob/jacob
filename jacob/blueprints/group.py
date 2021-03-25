"""Блок Студенты."""

from loguru import logger
from pony import orm
from vkwave import bots

from jacob.database.utils import admin, students
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


@bots.simple_bot_message_handler(
    group_router,
    filters.PLFilter({"button": "lists"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _start_lists(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    group_id = admin.get_active_group(admin_id).id

    with orm.db_session:
        kb = kbs.group.list_of_lists(group_id)

    await ans.answer(
        "Списки студентов группы",
        keyboard=kb,
    )
