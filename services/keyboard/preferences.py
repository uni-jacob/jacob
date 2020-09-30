import typing as t

import requests
from vkwave.bots import Keyboard

from services.keyboard import common

JSONStr = str


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
    kb = await common.list_of_chats(vk_id)
    if kb.buttons[-1]:
        kb.add_row()
    kb.add_text_button("➕ Зарегистрировать чат", payload={"button": "reg_chat"})
    kb.add_row()
    kb.add_text_button("◀️ Назад", payload={"button": "settings"})
    return kb.get_keyboard()


def configure_chat(chat_id: int):
    """
    Меню настройки чата

    Args:
        chat_id: Идентфикатор чата

    Returns:
        JSONStr: клавиатура
    """
    kb = Keyboard()
    kb.add_text_button(
        "🗑 Отключить чат", payload={"button": "remove_chat", "chat": chat_id}
    )
    kb.add_row()
    kb.add_text_button(
        "🗂 Индексировать чат", payload={"button": "index_chat", "chat": chat_id}
    )
    kb.add_row()
    kb.add_text_button("◀️ Назад", payload={"button": "configure_chats"})
    return kb.get_keyboard()


def index_chat(
    chat_id: int, vk_students: t.List[int], db_students: t.List[int]
) -> JSONStr:
    """
    Меню индексации чата

    Args:
        chat_id: Идентификатор чата
        vk_students: Список студентов, присутствующих в чате
        db_students: Список студентов, присутствующих в БД
    Returns:
        JSONStr: Клавиатура
    """
    kb = Keyboard()
    if vk_students:
        query = requests.post(
            "https://dpaste.com/api/v2/",
            data={
                "content": ",".join(map(str, vk_students)),
                "syntax": {"text": "Plain " "text"},
            },
        )
        link = query.text.strip("\n")
        kb.add_text_button(
            "➕ Зарегистрировать студентов",
            payload={
                "button": "register_students",
                "chat_id": chat_id,
                "students": link,
            },
        )
        kb.add_row()
    if db_students:
        query = requests.post(
            "https://dpaste.com/api/v2/",
            data={
                "content": ",".join(map(str, db_students)),
                "syntax": {"text": "Plain text"},
            },
        )
        link = query.text.strip("\n")
        kb.add_text_button(
            "➖ Удалить студентов",
            payload={
                "button": "purge_students",
                "chat_id": chat_id,
                "students": link,
            },
        )
        kb.add_row()
    kb.add_text_button(
        "◀️ Назад",
        payload={"button": "chat", "chat_id": chat_id},
    )
    return kb.get_keyboard()
