import os

from vkwave.api import API
from vkwave.bots import Keyboard
from vkwave.client import AIOHTTPClient

from database import utils as db

JSONStr = str
api_session = API(tokens=os.getenv("VK_TOKEN"), clients=AIOHTTPClient())
api = api_session.get_context()


def preferences() -> JSONStr:
    """
    Возвращает клавиатуру главного окна настроек
    Returns:
        JSONStr: клавиатура
    """
    kb = Keyboard()
    kb.add_text_button("💬 Настроить чаты", payload={"button": "configure_chats"})
    kb.add_row()
    kb.add_text_button("◀️ Назад", payload={"button": "main_menu"})

    return kb.get_keyboard()


async def connected_chats(vk_id: int) -> JSONStr:
    """
    Генерирует клавиатуру со списком подключенных чатов
    Args:
        vk_id: идентификатор пользователя
    Returns:
        JSONStr: клавиатура
    """
    kb = Keyboard()
    chats = db.chats.get_list_of_chats_by_group(vk_id)
    for chat in chats:
        chat_object = await api.messages.get_conversations_by_id(
            peer_ids=chat.chat_id, group_id=os.getenv("GROUP_ID")
        )
        try:
            chat_title = chat_object.response.items[0].chat_settings.title
        except AttributeError:
            chat_title = "???"
        kb.add_text_button(
            chat_title,
            payload={
                "button": "chat",
                "group": chat.group_id.id,
                "chat_type": chat.chat_type.id,
            },
        )
    kb.add_row()
    if len(chats) < 2:
        kb.add_text_button("➕ Зарегистрировать чат", payload={"button": "reg_chat"})
        kb.add_row()
    kb.add_text_button("◀️ Назад", payload={"button": "settings"})
    return kb.get_keyboard()
