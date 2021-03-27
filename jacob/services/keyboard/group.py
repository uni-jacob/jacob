from pony import orm
from vkwave.bots import Keyboard

from jacob.database.utils import lists, students
from jacob.services import keyboard as kbs
from jacob.services.keyboard.common import Keyboards, StudentsNavigator


class ListsKeyboards(Keyboards):
    """Набор клавиатур для навигации в режиме редактирования Списков."""

    def __init__(self, admin_id: int, return_to: str, list_id: int):
        super().__init__(admin_id)
        self.return_to = return_to
        self.list_id = list_id

    def menu(self) -> str:
        """
        Главное меню Списков (половины алфавита, сохранить, отменить).

        Returns:
            str: Клавиатура
        """
        kb = kbs.common.alphabet(self.admin_id)
        if len(kb.buttons[-1]):
            kb.add_row()
        kb.add_text_button(text="✅ Сохранить", payload={"button": "save"})

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
        with orm.db_session:
            data = students.get_list_of_students_by_letter(self.admin_id, letter)
            half_index = self._find_half_index_of_letter(letter)
            selected = lists.get_students_in_list(self.list_id)

            kb = Keyboard()
            for item in data:
                if len(kb.buttons[-1]) == 2:
                    kb.add_row()
                label = " "
                if item in selected:
                    label = "✅ "
                kb.add_text_button(
                    text=f"{label}{item.last_name} {item.first_name}",
                    payload={
                        "button": "student",
                        "student_id": item.id,
                        "letter": letter,
                        "name": f"{item.last_name} {item.first_name}",
                    },
                )
        if kb.buttons[-1]:
            kb.add_row()
        kb.add_text_button(
            text="◀️ Назад",
            payload={"button": "half", "half": half_index},
        )

        return kb.get_keyboard()


class ListNavigator(StudentsNavigator):
    def __init__(self, admin_id: int, list_id: int):
        super().__init__(admin_id)
        self.return_to = "edit_students_in_list"
        self.list_id = list_id

    def render(self):
        return ListsKeyboards(self.admin_id, self.return_to, self.list_id)


def group_menu():
    kb = Keyboard()
    kb.add_text_button(
        "Студенты",
        payload={"button": "students"},
    )
    kb.add_text_button("Списки", payload={"button": "lists"})
    kb.add_row()
    kb.add_text_button(
        text="◀️ Назад",
        payload={"button": "main_menu"},
    )

    return kb.get_keyboard()


@orm.db_session
def list_of_lists(group_id: int):
    kb = Keyboard()

    with orm.db_session:
        lists_of_group = lists.get_lists_of_group(group_id)

    for lst in lists_of_group:
        if len(kb.buttons[-1]) == 2:
            kb.add_row()
        kb.add_text_button(lst.name, payload={"button": "list", "list": lst.id})

    if kb.buttons[-1]:
        kb.add_row()

    kb.add_text_button(
        text="Создать список",
        payload={"button": "create_list"},
    )
    kb.add_row()
    kb.add_text_button(
        text="◀️ Назад",
        payload={"button": "group_mgmt"},
    )

    return kb.get_keyboard()


def list_menu():
    kb = Keyboard()

    kb.add_text_button("Переименовать", payload={"button": "rename_list"})
    kb.add_text_button("Список студентов", payload={"button": "edit_students_in_list"})
    kb.add_row()
    kb.add_text_button("Удалить список", payload={"button": "remove_list"})
    kb.add_row()
    kb.add_text_button(
        text="◀️ Назад",
        payload={"button": "lists"},
    )

    return kb.get_keyboard()
