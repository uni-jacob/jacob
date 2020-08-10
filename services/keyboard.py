from vkwave.bots.utils.keyboards import Keyboard

from database import utils


def main_menu(user_id: int) -> str:
    """
    Генерирует клавиатуру главного меню
    Args:
        user_id: Идентификатор пользователя
    Returns:
        JSON-like str: Строка с клавиатурой

    """
    is_admin = utils.is_user_admin(admin_id=utils.get_system_id_of_student(user_id))
    kb = Keyboard()
    if is_admin:
        kb.add_text_button(text="📢 Призыв", payload={"button": "call"})
        kb.add_text_button(text="💰 Финансы", payload={"button": "finances"})
        kb.add_row()
    kb.add_text_button(text="📅 Расписание", payload={"button": "schedule"})
    kb.add_text_button(text="📨 Рассылки", payload={"button": "mailings"})
    if is_admin:
        kb.add_row()
        kb.add_text_button(text="⚙ Настройки", payload={"button": "settings"})
        kb.add_text_button(text="🌐 Веб", payload={"button": "web"})
    return kb.get_keyboard()


def skip_call_message():
    """
    Генерирует клавиатуру для пропуска ввода сообщения призыва
    Returns:
        JSON-like str: Строка с клавиатурой
    """
    kb = Keyboard()
    kb.add_text_button(text="👉🏻 Пропустить", payload={"button": "skip_call_message"})

    kb.add_text_button(text="🚫 Отмена", payload={"button": "cancel_call"})
    return kb.get_keyboard()
