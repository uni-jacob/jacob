import typing as t

from vkwave.bots import Keyboard

from database import utils as db


def alphabet(user_id: int, category_id: t.Optional[int]) -> Keyboard:
    """
    Генерирует фрагмент клавиатуры со списком первых букв фамилиий студентов

    Args:
        user_id: Идентификатор администратора
        category_id: идентификатор категории (для возврата назад)

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
            payload = {"button": "half", "half": half}
            if category_id:
                payload["category"] = category_id
            kb.add_text_button(title, payload=payload)
    else:
        for letter in alphabet:
            if len(kb.buttons[-1]) == 4:
                kb.add_row()
            payload = {"button": "half", "value": letter}
            if category_id:
                payload["category"] = category_id
            kb.add_text_button(text=letter, payload=payload)

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
