import os

from vkbottle.keyboard import Keyboard
from vkbottle.keyboard import Text

from database import Database
from database import utils


class Keyboards:
    def __init__(self):
        self.db = Database(os.environ["DATABASE_URL"])

    @staticmethod
    async def main_menu(user_id: int) -> str:
        """
        Генерирует клавиатуру главного меню
        Args:
            user_id: Идентификатор пользователя
        Returns:
            JSON-like str: Строка с клавиатурой

        """
        is_admin = await utils.is_admin(user_id=user_id)
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
        kb.add_button(
            Text(label="👉🏻 Пропустить", payload={"button": "skip_call_message"})
        )
        kb.add_button(Text(label="🚫 Отмена", payload={"button": "cancel_call"}))
        return kb.generate()

    async def alphabet(self, user_id):
        """
        Генерирует фрагмент клавиатуры со списком первых букв фамилиий студентов

        Args:
            user_id: Идентификатор администратора

        Returns:
            Keyboard: Фрагмент клавиатуры
        """
        kb = Keyboard()
        kb.add_row()
        alphabet = await self.db.get_unique_second_name_letters(user_id)
        for letter in alphabet:
            if len(kb.buttons[-1]) == 4:
                kb.add_row()
            kb.add_button(
                Text(label=letter, payload={"button": "letter", "value": letter})
            )
        return kb

    async def call_interface(self, user_id: int):
        """
        Генерирует клавиатуру для выбора призываемых

        Args:
            user_id: Идентификатор пользователя

        Returns:
            JSON-like str: Строка с клавиатурой
        """
        kb = await self.alphabet(user_id)
        if len(kb.buttons[-1]):
            kb.add_row()
        kb.add_button(Text(label="✅ Сохранить", payload={"button": "save_selected"}))
        kb.add_button(Text(label="👥 Призвать всех", payload={"button": "call_all"}))
        kb.add_row()
        kb.add_button(Text(label="🚫 Отмена", payload={"button": "cancel_call"}))

        return kb.generate()

    async def list_of_students(self, letter: str, user_id: int):
        """
        Генерирует клавиатуру со списком студентов, фамилии которых начинаются на letter
        Args:
            letter: Первая буква фамилий
            user_id: Идентификатор пользователя

        Returns:
            JSON-like str: Строка с клавиатурой
        """
        data = await self.db.get_list_of_names(letter, user_id)
        kb = Keyboard()
        kb.add_row()
        for item in data:
            print(item)
            if len(kb.buttons[-1]) == 2:
                kb.add_row()
            kb.add_button(
                Text(
                    label=f"{item['second_name']} {item['first_name']}",
                    payload={
                        "button": "student",
                        "student_id": item["id"],
                        "name": f"{item['second_name']} {item['first_name']}",
                    },
                )
            )
        if kb.buttons[-1]:
            kb.add_row()
        kb.add_button(Text(label="Назад", payload={"button": "skip_call_message"}))
        return kb.generate()

    @staticmethod
    def prompt():
        """
        Генерирует клавиатуру с подтверждением действия
        Returns:
            Keyboard: Объект клавиатуры
        """
        kb = Keyboard()
        kb.add_row()
        kb.add_button(Text(label="✅ Подтвердить", payload={"button": "confirm"}))
        kb.add_button(Text(label="🚫 Отменить", payload={"button": "deny"}))
        return kb

    def call_prompt(self, names_usage: bool, chat_type: int):
        """
        Генерирует клавиатуру с подтверждением отправки призыва и возможностью его
        настройки

        Args:
            names_usage: Использование имен
            chat_type: Тип выбранного чата

        Returns:
            JSON-like str:  Клавиатура
        """
        kb = self.prompt()
        kb.add_row()
        if names_usage:
            names_emoji = "✅"
        else:
            names_emoji = "🚫"
        if chat_type:
            chat_emoji = "📡"
        else:
            chat_emoji = "🛠"
        kb.add_button(
            Text(
                label=f"{names_emoji} Использовать имена",
                payload={"button": "names_usage"},
            )
        )
        kb.add_button(
            Text(
                label=f"{chat_emoji} Переключить беседу",
                payload={"button": "chat_config"},
            )
        )
        return kb.generate()

    @staticmethod
    def settings():
        """
        Генерирует клавиатуру главного окна настроек

        Returns:
            JSON-like str: Строка с клавиатурой
        """
        kb = Keyboard()
        kb.add_row()
        kb.add_button(Text(label="💬 Чаты", payload={"button": "chat_settings"}))
        kb.add_button(
            Text(label="Локальные настройки", payload={"button": "local_settings"})
        )
        kb.add_row()
        kb.add_button(Text(label="👈🏻 Назад", payload={"button": "home"}))
        return kb.generate()
