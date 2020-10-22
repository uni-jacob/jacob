import typing as t

from vkwave.bots import Keyboard

from database import utils as db
from services import keyboard as kbs

JSONStr = str


def skip_call_message() -> JSONStr:
    """
    Генерирует клавиатуру для пропуска ввода сообщения призыва.

    Returns:
        JSONStr: Строка с клавиатурой
    """
    kb = Keyboard()
    kb.add_text_button(text="⏩ Пропустить", payload={"button": "skip_call_message"})

    kb.add_text_button(text="🚫 Отмена", payload={"button": "cancel_call"})
    return kb.get_keyboard()


def call_interface(admin_id: int) -> JSONStr:
    """
    Генерирует клавиатуру для выбора призываемых.

    Args:
        admin_id: Идентификатор пользователя

    Returns:
        JSONStr: Строка с клавиатурой
    """
    kb = kbs.common.alphabet(admin_id)
    if len(kb.buttons[-1]):
        kb.add_row()
    kb.add_text_button(text="✅ Сохранить", payload={"button": "save_selected"})
    kb.add_text_button(text="👥 Призвать всех", payload={"button": "call_all"})
    kb.add_row()
    kb.add_text_button(text="✏️ Изменить текст", payload={"button": "call"})
    kb.add_row()
    kb.add_text_button(text="🚫 Отмена", payload={"button": "cancel_call"})

    return kb.get_keyboard()


def list_of_letters(
    letters: list,
    return_to: str = "skip_call_message",
    category_id: int = None,
) -> JSONStr:
    """
    Генерирует подменю с буквами алфавита.

    Args:
        letters: список букв
        return_to: Пейлоад с указанием места возврата
        category_id: идшник категории финансов (используется для возврата назад в
            добавление дохода)

    Returns:
        JSONStr: клавиатура
    """
    kb = Keyboard()
    for letter in letters:
        if len(kb.buttons[-1]) == 4:
            kb.add_row()
        kb.add_text_button(
            letter,
            payload={
                "button": "letter",
                "value": letter,
                "letters": letters,
            },
        )
    if kb.buttons[-1]:
        kb.add_row()
    payload = {"button": return_to}
    if category_id:
        payload["category"] = category_id
    kb.add_text_button("◀️ Назад", payload=payload)
    return kb.get_keyboard()


def list_of_students(
    letter: str,
    admin_id: int,
    letters: t.Optional[t.List[str]] = None,
) -> JSONStr:
    """
    Генерирует клавиатуру со списком студентов, фамилии которых начинаются на letter.

    Args:
        letter: Первая буква фамилий
        admin_id: Идентификатор пользователя
        letters: Список букв (передается когда существует подменю из диапазонов букв,
            используется для возврата назад)

    Returns:
        JSONStr: Строка с клавиатурой
    """
    data = db.students.get_list_of_students_by_letter(letter, admin_id)
    selected = db.shortcuts.get_list_of_calling_students(admin_id)
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
    if letters:
        kb.add_text_button(text="◀️ Назад", payload={"button": "half", "half": letters})
    else:
        kb.add_text_button(text="◀️ Назад", payload={"button": "skip_call_message"})
    return kb.get_keyboard()


def call_prompt(admin_id: int) -> JSONStr:
    """
    Генерирует клавиатуру с настройкой призыва.

    Args:
        admin_id: идентфикатор администратора

    Returns:
        JSONStr:  Клавиатура
    """
    kb = kbs.common.prompt()
    kb.add_row()
    store = db.admin.get_admin_storage(admin_id)
    if store.names_usage:
        names_emoji = "✅"
    else:
        names_emoji = "🚫"
    chat_emoji = "📡"
    kb.add_text_button(
        text=f"{names_emoji} Использовать имена",
        payload={"button": "names_usage"},
    )
    kb.add_text_button(
        text=f"{chat_emoji} Переключить чат",
        payload={"button": "chat_config"},
    )
    return kb.get_keyboard()
