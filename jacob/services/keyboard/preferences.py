from pony import orm
from vkwave.bots import Keyboard

from jacob.database.utils import admin, groups
from jacob.services.keyboard import common

JSONStr = str


def preferences(admin_id: int) -> JSONStr:
    """
    Возвращает клавиатуру главного окна настроек.

    Args:
        admin_id: Идентификатор администратора

    Returns:
        JSONStr: клавиатура
    """
    kb = Keyboard()
    kb.add_text_button("💬 Настроить чаты", payload={"button": "configure_chats"})
    kb.add_row()

    with orm.db_session:
        feud = admin.get_admin_feud(admin_id)
        if len(feud) > 1:
            kb.add_text_button("Выбрать группу", payload={"button": "select_group"})
            kb.add_row()

    kb.add_text_button("🔒 Публичность группы", payload={"button": "change_publicity"})
    kb.add_row()

    kb.add_text_button("◀️ Назад", payload={"button": "main_menu"})

    return kb.get_keyboard()


async def connected_chats(api_context, admin_id: int) -> JSONStr:
    """
    Генерирует клавиатуру со списком подключенных чатов.

    Args:
        api_context: Объект API ВК.
        admin_id: идентификатор пользователя

    Returns:
        JSONStr: клавиатура
    """
    kb = await common.list_of_chats(api_context, admin_id)
    if kb.buttons[-1]:
        kb.add_row()
    kb.add_text_button("➕ Зарегистрировать чат", payload={"button": "reg_chat"})
    kb.add_row()
    kb.add_text_button("◀️ Назад", payload={"button": "settings"})
    return kb.get_keyboard()


def configure_chat(chat_id: int):
    """
    Меню настройки чата.

    Args:
        chat_id: Идентфикатор чата

    Returns:
        JSONStr: клавиатура
    """
    kb = Keyboard()
    kb.add_text_button(
        "🗑 Отключить чат",
        payload={"button": "remove_chat", "chat": chat_id},
    )
    kb.add_row()
    kb.add_text_button(
        "🗂 Индексировать чат",
        payload={"button": "index_chat", "chat": chat_id},
    )
    kb.add_row()
    kb.add_text_button(
        "◀️ Назад",
        payload={"button": "configure_chats"},
    )
    return kb.get_keyboard()


def index_chat(
    chat_id: int,
) -> JSONStr:
    """
    Меню индексации чата.

    Args:
        chat_id: Идентификатор чата

    Returns:
        JSONStr: Клавиатура
    """
    kb = Keyboard()
    kb.add_text_button(
        "➕ Зарегистрировать студентов",
        payload={
            "button": "register_students",
            "chat_id": chat_id,
        },
    )
    kb.add_row()
    kb.add_text_button(
        "➖ Удалить студентов",
        payload={
            "button": "purge_students",
            "chat_id": chat_id,
        },
    )
    kb.add_row()
    kb.add_text_button(
        "◀️ Назад",
        payload={"button": "chat", "chat_id": chat_id},
    )
    return kb.get_keyboard()


def list_of_groups(admin_id: int) -> JSONStr:
    """
    Генерирует клавиатуру с группами, доступных пользователю для администрирования.

    Args:
        admin_id: идентификатор администратора

    Returns:
        JSONStr: Строка с клавиатурой
    """
    kb = Keyboard()

    groups = admin.get_admin_feud(admin_id)
    for group in groups:
        if len(kb.buttons[-1]) == 2:
            kb.add_row()
        kb.add_text_button(
            group.group_num,
            payload={"button": "group", "group_id": group.id},
        )

    return kb.get_keyboard()


def group_privacy(group_id: int) -> JSONStr:
    kb = Keyboard()

    privacy = groups.get_privacy_of_group(group_id)

    if privacy:
        kb.add_text_button(
            "🔓 Публичная", payload={"button": "change_group_privacy", "value": False}
        )
    else:
        kb.add_text_button(
            "🔒 Приватная", payload={"button": "change_group_privacy", "value": True}
        )

    kb.add_row()
    kb.add_text_button(
        "◀️ Назад",
        payload={"button": "main_menu"},
    )

    return kb.get_keyboard()
