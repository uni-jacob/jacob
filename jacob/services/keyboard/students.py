from pony import orm
from vkwave.bots import Keyboard

from jacob.database.utils import students


def student_card(is_admin):
    kb = Keyboard()

    kb.add_text_button(
        "☎ Контакты",
        payload={"button": "get_contacts"},
    )
    kb.add_text_button(
        "✏ Редактировать",
        payload={"button": "edit_student"},
    )

    kb.add_row()
    kb.add_text_button("🔥 Удалить", payload={"button": "delete_student"})

    if is_admin:
        kb.add_text_button("🔒 Разжаловать", payload={"button": "demote_admin"})
    else:
        kb.add_text_button("🔓 Назначить админом", payload={"button": "make_admin"})

    kb.add_row()
    kb.add_text_button("◀️ Назад", payload={"button": "letter"})

    return kb.get_keyboard()


def edit_menu():
    kb = Keyboard()

    kb.add_text_button("Имя", payload={"button": "edit_name"})
    kb.add_text_button("Фамилия", payload={"button": "edit_surname"})
    kb.add_row()
    kb.add_text_button("Подгруппа", payload={"button": "edit_subgroup"})
    kb.add_text_button("Телефон", payload={"button": "edit_phone"})
    kb.add_row()
    kb.add_text_button("Электропочта", payload={"button": "edit_email"})
    kb.add_text_button("Форма обучения", payload={"button": "edit_academic_status"})
    kb.add_row()
    kb.add_text_button("◀️ Назад", payload={"button": "get_contacts"})

    return kb.get_keyboard()


def list_of_academic_statuses():

    kb = Keyboard()

    with orm.db_session:
        ac_statuses = students.get_academic_statuses()

    for status in ac_statuses:
        if len(kb.buttons[-1]) == 2:
            kb.add_row()

        kb.add_text_button(
            status.description,
            payload={"button": "students_new_status", "status": status.id},
        )

    kb.add_row()
    kb.add_text_button("🚫 Отмена", payload={"button": "cancel"})

    return kb.get_keyboard()
