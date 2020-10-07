import os

from loguru import logger
from vkwave.api import API
from vkwave.bots import Keyboard
from vkwave.client import AIOHTTPClient

from database import utils as db
from services import keyboard as kbs
from services.logger.config import config

JSONStr = str
api_session = API(tokens=os.getenv("VK_TOKEN"), clients=AIOHTTPClient())
api = api_session.get_context()
logger.configure(**config)


def list_of_fin_categories(vk_id: int) -> JSONStr:
    kb = Keyboard()
    admin_id = db.students.get_system_id_of_student(vk_id)
    categories = db.finances.get_list_of_fin_categories(
        db.admin.get_active_group(admin_id)
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


def fin_category() -> JSONStr:
    """
    клавиатура меню категории финансов

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


def fin_list_of_letters(user_id: int):

    kb = kbs.common.alphabet(user_id)

    if kb.buttons[-1]:
        kb.add_row()

    kb.add_text_button("🚫 Отмена", payload={"button": "fin_category"})

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
