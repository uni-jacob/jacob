import os

from loguru import logger
from pony import orm
from vkwave.api import API
from vkwave.bots import Keyboard
from vkwave.client import AIOHTTPClient

from jacob.database.utils import admin, finances
from jacob.database.utils.storages import managers
from jacob.services import keyboard as kbs
from jacob.services.keyboard.common import Keyboards, StudentsNavigator
from jacob.services.logger.config import config

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
        store = managers.FinancialConfigManager(self.admin_id).get_or_create()
        if len(kb.buttons[-1]):
            kb.add_row()
        kb.add_text_button(
            text="🚫 Отмена",
            payload={"button": "fin_category", "category": store.financial_category.id},
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
    with orm.db_session:
        categories = finances.get_fin_categories(admin.get_active_group(admin_id))
        for category in categories:
            if len(kb.buttons[-1]) == 2:
                kb.add_row()
            kb.add_text_button(
                category.name,
                payload={"button": "fin_category", "category": category.id},
            )
    if kb.buttons[-1]:
        kb.add_row()
    kb.add_text_button(
        "➕ Создать категорию",
        payload={"button": "create_finances_category"},
    )
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
    kb.add_text_button("Настройки", payload={"button": "finances_pref"})
    kb.add_row()
    kb.add_text_button("◀️ Назад", payload={"button": "finances"})

    return kb.get_keyboard()


def fin_prefs() -> JSONStr:
    """Настройки фин. категории.

    Returns:
        JSONStr: клавиатура
    """
    kb = Keyboard()

    kb.add_text_button("Переименовать", payload={"button": "rename_fin_cat"})
    kb.add_text_button("Изменить сумму", payload={"button": "change_fin_sum"})
    kb.add_row()
    kb.add_text_button("Уведомить", payload={"button": "send_fin_alert"})
    kb.add_text_button("Удалить", payload={"button": "delete_fin_cat"})
    kb.add_row()
    kb.add_text_button("◀️ Назад", payload={"button": "fin_category"})

    return kb.get_keyboard()
