import os

from vkwave.api import API
from vkwave.bots import Keyboard
from vkwave.client import AIOHTTPClient

from database import utils as db

JSONStr = str
api_session = API(tokens=os.getenv("VK_TOKEN"), clients=AIOHTTPClient())
api = api_session.get_context()


def alphabet(group_id: int) -> Keyboard:
    """
    Генерирует фрагмент клавиатуры с половинами алфавита фамилиий студентов.

    Args:
        admin_id: Идентификатор администратора

    Returns:
        Keyboard: Фрагмент клавиатуры
    """
    kb = Keyboard()
    alphabet = db.students.get_unique_second_name_letters_in_a_group(
        db.admin.get_active_group(admin_id),
    )
    if len(alphabet) > 15:
        half_len = len(alphabet) // 2
        f_alphabet, s_alphabet = alphabet[:half_len], alphabet[half_len:]
        for half in (f_alphabet, s_alphabet):
            title = f"{half[0]}..{half[-1]}"
            kb.add_text_button(title, payload={"button": "half", "half": half})
    else:
        for letter in alphabet:
            if len(kb.buttons[-1]) == 4:
                kb.add_row()
            kb.add_text_button(
                text=letter,
                payload={"button": "letter", "value": letter},
            )

    return kb


async def list_of_chats(admin_id: int):
    """
    Генерирует фрагмент клавиатуры со списком подключенных чатов.

    Args:
        admin_id: идентификатор пользователя

    Returns:
        Keyboard: Фрагмент клавиатуры
    """
    kb = Keyboard()

    chats = db.chats.get_list_of_chats_by_group(
        db.admin.get_active_group(admin_id),
    )
    for chat in chats:
        chat_object = await api.messages.get_conversations_by_id(
            peer_ids=chat.chat_id,
            group_id=os.getenv("GROUP_ID"),
        )
        try:
            chat_title = chat_object.response.items[0].chat_settings.title
        except (AttributeError, IndexError):
            chat_title = "???"
        kb.add_text_button(
            chat_title,
            payload={
                "button": "chat",
                "chat_id": chat.id,
            },
        )
    return kb


def prompt() -> Keyboard:
    """
    Генерирует клавиатуру с подтверждением действия.

    Returns:
        Keyboard: Объект клавиатуры
    """
    kb = Keyboard()
    kb.add_text_button(text="✅ Подтвердить", payload={"button": "confirm"})
    kb.add_text_button(text="🚫 Отменить", payload={"button": "deny"})
    return kb


def empty() -> JSONStr:
    kb = Keyboard()

    return kb.get_empty_keyboard()


def cancel():
    """
    Генерирует клавиатуру для отмены действия.

    Returns:
        JSONStr: клавиатура
    """
    kb = Keyboard()

    kb.add_text_button("Отмена", payload={"button": "cancel"})

    return kb.get_keyboard()
