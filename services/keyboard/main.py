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
        kb.add_row()
        kb.add_text_button(text="⚙ Настройки", payload={"button": "settings"})
        kb.add_text_button(text="🌐 Веб", payload={"button": "web"})
    return kb.get_keyboard()
