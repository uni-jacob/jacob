from vkwave.bots import Keyboard

from jacob.database.utils.storages import managers
from jacob.services import keyboard as kbs
from jacob.services.keyboard.common import Keyboards, StudentsNavigator

JSONStr = str


class CallKeyboards(Keyboards):
    """Набор клавиатур для навигации в режиме Призыва."""

    def __init__(self, admin_id: int, return_to: str):
        super().__init__(admin_id)
        self.return_to = return_to

    def menu(self) -> str:
        """
        Главное меню призыва (половины алфавита, сохранить, отменить, изменить).

        Returns:
            str: Клавиатура
        """
        kb = kbs.common.alphabet(self.admin_id)
        if len(kb.buttons[-1]):
            kb.add_row()
        kb.add_text_button(text="✅ Сохранить", payload={"button": "save_selected"})
        kb.add_text_button(text="Пресеты", payload={"button": "presets"})
        kb.add_row()
        kb.add_text_button(text="✏️ Изменить текст", payload={"button": "call"})
        kb.add_row()
        kb.add_text_button(text="🚫 Отмена", payload={"button": "cancel_call"})

        return kb.get_keyboard()

    def submenu(self, half: int) -> str:
        """
        Подменю призыва (список букв в рамках половины алфавита).

        Returns:
            str: Клавиатура

        """
        kb = super().submenu(half)
        return kb

    def students(self, letter: str) -> str:
        """
        Список студентов на букву.

        Args:
            letter: Первая буква фамилии для поиска студентов

        Returns:
            str: Клавиатура

        """
        kb = super().students(letter)
        return kb


class CallNavigator(StudentsNavigator):
    def __init__(self, admin_id: int):
        super().__init__(admin_id)
        self.return_to = "skip_call_message"

    def render(self):
        return CallKeyboards(self.admin_id, self.return_to)


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


def call_prompt(admin_id: int) -> JSONStr:
    """
    Генерирует клавиатуру с настройкой призыва.

    Args:
        admin_id: идентификатор администратора

    Returns:
        JSONStr:  Клавиатура
    """
    kb = kbs.common.prompt()
    kb.add_row()
    store = managers.AdminConfigManager(admin_id)
    if store.get_names_usage():
        names_emoji = "✅"
    else:
        names_emoji = "🚫"
    chat_emoji = "📡"
    kb.add_text_button(text="◀️ Назад", payload={"button": "skip_call_message"})
    kb.add_row()
    kb.add_text_button(
        text=f"{names_emoji} Использовать имена",
        payload={"button": "names_usage"},
    )
    kb.add_text_button(
        text=f"{chat_emoji} Переключить чат",
        payload={"button": "chat_config"},
    )
    return kb.get_keyboard()


def presets():
    kb = Keyboard()

    kb.add_text_button(text="Все студенты", payload={"button": "call_all"})
    kb.add_text_button("Подгруппы", payload={"button": "subgroups"})
    kb.add_row()
    kb.add_text_button("Формы обучения", payload={"button": "academic_statuses"})
    kb.add_row()
    kb.add_text_button("Пользовательские пресеты", payload={"button": "custom_presets"})
    kb.add_row()
    kb.add_text_button(text="◀️ Назад", payload={"button": "skip_call_message"})

    return kb.get_keyboard()
