from loguru import logger
from vkwave.bots import Keyboard

from database import utils as db

JSONStr = str


def main_menu(admin_id: int) -> JSONStr:
    """
    Генерирует клавиатуру главного меню.

    Args:
        admin_id: Идентификатор пользователя

    Returns:
        JSONStr: Строка с клавиатурой

    """
    is_admin = db.admin.is_user_admin(admin_id)
    logger.debug(f"{is_admin=}")
    kb = Keyboard()
    if is_admin:
        kb.add_text_button(text="📢 Призыв", payload={"button": "call"})
        kb.add_text_button(text="💰 Финансы", payload={"button": "finances"})
        kb.add_row()
    kb.add_text_button(text="📅 Расписание", payload={"button": "schedule"})
    if is_admin:
        kb.add_text_button(text="📕 Контакты", payload={"button": "contacts"})
        kb.add_row()
        kb.add_text_button(text="⚙ Настройки", payload={"button": "settings"})
        kb.add_text_button(text="🌐 Веб", payload={"button": "web"})
        kb.add_row()
        kb.add_text_button(
            text="⚠ Сообщить об ошибке",
            payload={"button": "report_error"},
        )
    return kb.get_keyboard()


def choose_register_way() -> JSONStr:
    kb = Keyboard()

    kb.add_text_button(
        text="Новая группа",
        payload={"button": "create_new_group"},
    )
    kb.add_text_button(
        text="Существующая группа",
        payload={"button": "choose_existing_group"},
    )

    return kb.get_keyboard()


def universities() -> JSONStr:
    kb = Keyboard()

    universities = db.uni.get_all()

    for uni in universities:
        if len(kb.buttons[-1] == 2):
            kb.add_row()

        kb.add_text_button(
            uni.name,
            payload={
                "button": "university",
                "university": uni.id,
            },
        )

    return kb.get_keyboard()
