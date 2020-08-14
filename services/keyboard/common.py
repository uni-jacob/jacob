from vkwave.bots import Keyboard

from database import utils as db


def alphabet(user_id: int) -> Keyboard:
    """
    Генерирует фрагмент клавиатуры со списком первых букв фамилиий студентов

    Args:
        user_id: Идентификатор администратора

    Returns:
        Keyboard: Фрагмент клавиатуры
    """
    kb = Keyboard()
    alphabet = db.students.get_unique_second_name_letters_in_a_group(user_id)
    for letter in alphabet:
        if len(kb.buttons[-1]) == 4:
            kb.add_row()
        kb.add_text_button(text=letter, payload={"button": "letter", "value": letter})

    return kb


def prompt() -> Keyboard:
    """
    Генерирует клавиатуру с подтверждением действия
    Returns:
        Keyboard: Объект клавиатуры
    """
    kb = Keyboard()
    kb.add_text_button(text="✅ Подтвердить", payload={"button": "confirm"})
    kb.add_text_button(text="🚫 Отменить", payload={"button": "deny"})
    return kb
