import os

from vkbottle.keyboard import Keyboard
from vkbottle.keyboard import Text

from database.db import Database


class Keyboards:
    def __init__(self):
        self.db = Database(os.environ["DATABASE_URL"])

    def main_menu(self, user_id: int) -> str:
        """
        Генерирует клавиатуру главного меню
        Args:
            user_id: Идентификатор пользователя
        Returns:
            JSON-like str: Строка с клавиатурой

        """
        is_admin = self.db.is_admin(user_id=user_id)
        kb = Keyboard()
        if is_admin:
            kb.add_row()
            kb.add_button(Text(label="📢 Призыв", payload={"button": "call"}))
            kb.add_button(Text(label="💰 Финансы", payload={"button": "finances"}))
        kb.add_row()
        kb.add_button(Text(label="📅 Расписание", payload={"button": "schedule"}))
        kb.add_button(Text(label="📨 Рассылки", payload={"button": "mailings"}))
        if is_admin:
            kb.add_row()
            kb.add_button(Text(label="⚙ Настройки", payload={"button": "settings"}))
            kb.add_button(Text(label="🌐 Веб", payload={"button": "web"}))
        return kb.generate()
