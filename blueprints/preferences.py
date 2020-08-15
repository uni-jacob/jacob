from vkwave.bots import DefaultRouter
from vkwave.bots import SimpleBotEvent
from vkwave.bots import simple_bot_message_handler

from services import filters
from database import utils as db
from services import keyboard as kbs

preferences_router = DefaultRouter()


@simple_bot_message_handler(
    preferences_router, filters.PLFilter({"button": "settings"})
)
async def open_preferences(ans: SimpleBotEvent):
    group_id = db.admin.get_admin_feud(
        db.students.get_system_id_of_student(ans.object.object.message.peer_id)
    )
    group = db.groups.find_group(id=group_id)
    await ans.answer(
        f"Настройки группы {group.group_num} ({group.specialty})",
        keyboard=kbs.preferences.preferences(),
    )


@simple_bot_message_handler(
    preferences_router, filters.PLFilter({"button": "configure_chats"})
)
async def list_of_chats(ans: SimpleBotEvent):
    await ans.answer(
        "Список подключенных чатов",
        keyboard=await kbs.preferences.connected_chats(
            ans.object.object.message.peer_id
        ),
    )
