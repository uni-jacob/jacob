from vkwave.bots import Keyboard

from database import utils as db

JSONStr = str


def alphabet(user_id: int) -> Keyboard:
    """
    Генерирует фрагмент клавиатуры со списком первых букв фамилиий студентов

    Args:
        user_id: Идентификатор администратора

    Returns:
        Keyboard: Фрагмент клавиатуры
    TODO:
        Вытащить вычисление алфавита в бота, ради переиспользуемости функции
    """
    kb = Keyboard()
    alphabet = db.students.get_unique_second_name_letters_in_a_group(user_id)
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
            kb.add_text_button(text=letter, payload={"button": "half", "value": letter})

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


def empty() -> JSONStr:
    kb = Keyboard()

    return kb.get_empty_keyboard()
