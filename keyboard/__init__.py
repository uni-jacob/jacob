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

    @staticmethod
    def skip_call_message():
        """
        Генерирует клавиатуру для пропуска ввода сообщения призыва
        Returns:
            JSON-like str: Строка с клавиатурой
        """
        kb = Keyboard()
        kb.add_row()
        kb.add_button(Text(label="Пропустить", payload={"button": "skip_call_message"}))
        return kb.generate()

    def alphabet(self, user_id):
        """
        Генерирует фрагмент клавиатуры со списком первых букв фамилиий студентов

        Args:
            user_id: Идентификатор администратора

        Returns:
            Keyboard: Фрагмент клавиатуры
        """
        kb = Keyboard()
        kb.add_row()
        alphabet = self.db.get_unique_second_name_letters(user_id)
        for letter in alphabet:
            if len(kb.buttons[-1]) == 4:
                kb.add_row()
            kb.add_button(
                Text(label=letter, payload={"button": "letter", "value": letter})
            )
        return kb

    def call_interface(self, user_id: int):
        """
        Генерирует клавиатуру для выбора призываемых

        Args:
            user_id: Идентификатор пользователя

        Returns:
            JSON-like str: Строка с клавиатурой
        """
        kb = self.generate_alphabet(user_id)
        if len(kb.buttons[-1]):
            kb.add_row()
        kb.add_button(Text(label="Сохранить", payload={"button": "save_selected"}))
        kb.add_button(Text(label="Призвать всех", payload={"button": "call_all"}))
        kb.add_row()
        kb.add_button(Text(label="Отмена", payload={"button": "cancel_call"}))

        return kb.generate()
