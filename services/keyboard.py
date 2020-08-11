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


def alphabet(user_id):
    """
    Генерирует фрагмент клавиатуры со списком первых букв фамилиий студентов

    Args:
        user_id: Идентификатор администратора

    Returns:
        Keyboard: Фрагмент клавиатуры
    """
    kb = Keyboard()
    alphabet = utils.get_unique_second_name_letters_in_a_group(user_id)
    for letter in alphabet:
        if len(kb.buttons[-1]) == 4:
            kb.add_row()
        kb.add_text_button(text=letter, payload={"button": "letter", "value": letter})

    return kb


def call_interface(user_id: int):
    """
    Генерирует клавиатуру для выбора призываемых

    Args:
        user_id: Идентификатор пользователя

    Returns:
        JSON-like str: Строка с клавиатурой
    """
    kb = alphabet(user_id)
    if len(kb.buttons[-1]):
        kb.add_row()
    kb.add_text_button(text="✅ Сохранить", payload={"button": "save_selected"})
    kb.add_text_button(text="👥 Призвать всех", payload={"button": "call_all"})
    kb.add_row()
    kb.add_text_button(text="🚫 Отмена", payload={"button": "cancel_call"})

    return kb.get_keyboard()


def list_of_students(letter: str, user_id: int):
    """
    Генерирует клавиатуру со списком студентов, фамилии которых начинаются на letter
    Args:
        letter: Первая буква фамилий
        user_id: Идентификатор пользователя

    Returns:
        JSON-like str: Строка с клавиатурой
    """
    data = utils.get_list_of_students_by_letter(letter, user_id)
    selected = utils.get_list_of_calling_students(
        utils.get_system_id_of_student(user_id)
    )
    kb = Keyboard()
    for item in data:
        if len(kb.buttons[-1]) == 2:
            kb.add_row()
        label = " "
        if item.id in selected:
            label = "✅ "
        kb.add_text_button(
            text=f"{label}{item.second_name} {item.first_name}",
            payload={
                "button": "student",
                "student_id": item.id,
                "letter": letter,
                "name": f"{item.second_name} {item.first_name}",
            },
        )
    if kb.buttons[-1]:
        kb.add_row()
    kb.add_text_button(text="Назад", payload={"button": "skip_call_message"})
    return kb.get_keyboard()


def prompt():
    """
    Генерирует клавиатуру с подтверждением действия
    Returns:
        Keyboard: Объект клавиатуры
    """
    kb = Keyboard()
    kb.add_text_button(text="✅ Подтвердить", payload={"button": "confirm"})
    kb.add_text_button(text="🚫 Отменить", payload={"button": "deny"})
    return kb


def call_prompt(admin_id: int):
    """
    Генерирует клавиатуру с подтверждением отправки призыва и возможностью его
    настройки

    Args:
        admin_id: идентфикатор администратора

    Returns:
        JSON-like str:  Клавиатура
    """
    kb = prompt()
    kb.add_row()
    store = utils.get_admin_storage(admin_id)
    if store.names_usage:
        names_emoji = "✅"
    else:
        names_emoji = "🚫"
    if store.current_chat:
        chat_emoji = "📡"
    else:
        chat_emoji = "🛠"
    kb.add_text_button(
        text=f"{names_emoji} Использовать имена", payload={"button": "names_usage"},
    )
    kb.add_text_button(
        text=f"{chat_emoji} Переключить беседу", payload={"button": "chat_config"},
    )
    return kb.get_keyboard()
