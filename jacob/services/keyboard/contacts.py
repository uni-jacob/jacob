from jacob.services import keyboard as kbs
from jacob.services.keyboard.common import Keyboards, StudentsNavigator


class ContactsKeyboards(Keyboards):
    """Набор клавиатур для навигации в режиме Контактов."""

    def __init__(self, admin_id: int, return_to: str):
        super().__init__(admin_id)
        self.return_to = return_to

    def menu(self) -> str:
        """
        Главное меню Контактов (половины алфавита, сохранить, отменить, изменить).

        Returns:
            str: Клавиатура
        """
        kb = kbs.common.alphabet(self.admin_id)
        if len(kb.buttons[-1]):
            kb.add_row()
        kb.add_text_button(
            text="🚫 Отмена",
            payload={"button": "main_menu"},
        )

        return kb.get_keyboard()

    def submenu(self, half: int) -> str:
        """
        Подменю Контактов (список букв в рамках половины алфавита).

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


class ContactsNavigator(StudentsNavigator):
    def __init__(self, admin_id: int):
        super().__init__(admin_id)
        self.return_to = "students"

    def render(self):
        return ContactsKeyboards(self.admin_id, self.return_to)
