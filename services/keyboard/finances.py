import os

from loguru import logger
from vkwave.api import API
from vkwave.bots import Keyboard
from vkwave.client import AIOHTTPClient

from database import utils as db
from services import keyboard as kbs
from services.keyboard.common import Keyboards
from services.keyboard.common import StudentsNavigator
from services.logger.config import config

JSONStr = str
api_session = API(tokens=os.getenv("VK_TOKEN"), clients=AIOHTTPClient())
api = api_session.get_context()
logger.configure(**config)


class IncomeKeyboards(Keyboards):
    """Набор клавиатур для навигации в режиме Добавления дохода."""

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
        store = db.admin.get_admin_storage(self.admin_id)
        if len(kb.buttons[-1]):
            kb.add_row()
        kb.add_text_button(
            text="🚫 Отмена",
            payload={"button": "fin_category", "category": store.category_id},
        )

        return kb.get_keyboard()

    def submenu(self, half: int) -> str:
        """
        Подменю добавления дохода (список букв в рамках половины алфавита).

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


class IncomeNavigator(StudentsNavigator):
    def __init__(self, admin_id: int):
        super().__init__(admin_id)
        self.return_to = "add_income"

    def render(self):
        return IncomeKeyboards(self.admin_id, self.return_to)


def list_of_fin_categories(admin_id: int) -> JSONStr:
    """
    Генерирует клавитуру со списком финансовых категорий.

    Args:
        admin_id: Идентификатор администратора

    Returns:
        JSONStr: клавиатура
    """
    kb = Keyboard()
    categories = db.finances.get_fin_categories(db.admin.get_active_group(admin_id))
    for category in categories:
        if len(kb.buttons[-1]) == 2:
            kb.add_row()
        kb.add_text_button(
            category.name,
            payload={"button": "fin_category", "category": category.id},
        )
    if kb.buttons[-1]:
        kb.add_row()
    kb.add_text_button("◀️ Назад", payload={"button": "main_menu"})

    return kb.get_keyboard()


def fin_category() -> JSONStr:
    """
    клавиатура меню категории финансов.

    Returns:
        JSONStr: клавиатура
    """
    kb = Keyboard()

    kb.add_text_button("📈 Доход", payload={"button": "add_income"})
    kb.add_text_button("📉 Расход", payload={"button": "add_expense"})
    kb.add_row()
    kb.add_text_button("💸 Должники", payload={"button": "show_debtors"})
    kb.add_text_button("📊 Статистика", payload={"button": "show_stats"})
    kb.add_row()
    kb.add_text_button("◀️ Назад", payload={"button": "finances"})

    return kb.get_keyboard()


def confirm_debtors_call():

    kb = kbs.common.prompt()

    if kb.buttons[-1]:
        kb.add_row()

    chat_emoji = "📡"
    kb.add_text_button(
        text=f"{chat_emoji} Переключить чат",
        payload={"button": "chat_config"},
    )

    return kb.get_keyboard()
