from pony import orm
from vkwave.bots import Keyboard

from jacob.database.utils import lists


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
    kb.add_text_button(
        text="◀️ Назад",
        payload={"button": "lists"},
    )

    return kb.get_keyboard()
