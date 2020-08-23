import os

from loguru import logger
from vkwave.api import API
from vkwave.bots import Keyboard
from vkwave.client import AIOHTTPClient

from database import utils as db
from services.logger.config import config

JSONStr = str
api_session = API(tokens=os.getenv("VK_TOKEN"), clients=AIOHTTPClient())
api = api_session.get_context()
logger.configure(**config)


def list_of_fin_categories(vk_id: int) -> JSONStr:
    kb = Keyboard()
    admin_id = db.students.get_system_id_of_student(vk_id)
    categories = db.finances.get_list_of_fin_categories(
        db.admin.get_admin_feud(admin_id)
    )
    for category in categories:
        if len(kb.buttons[-1]) == 2:
            kb.add_row()
        kb.add_text_button(
            category.name, payload={"button": "fin_category", "category": category.id}
        )
    if kb.buttons[-1]:
        kb.add_row()
    kb.add_text_button("◀️ Назад", payload={"button": "main_menu"})

    return kb.get_keyboard()


def fin_category(category_id: int) -> JSONStr:
    """
    клавиатура меню категории финансов
    Args:
        category_id: идентификатор клавиатуры

    Returns:
        JSONStr: клавиатура
    """
    kb = Keyboard()

    kb.add_text_button(
        "📈 Доход", payload={"button": "add_income", "category": category_id}
    )
    kb.add_text_button(
        "📉 Расход", payload={"button": "add_expense", "category": category_id}
    )
    kb.add_row()
    kb.add_text_button(
        "💸 Должники", payload={"button": "show_debtors", "category": category_id}
    )
    kb.add_text_button(
        "📊 Статистика", payload={"button": "show_stats", "category": category_id}
    )
    kb.add_row()
    kb.add_text_button("◀️ Назад", payload={"button": "finances"})

    return kb.get_keyboard()
