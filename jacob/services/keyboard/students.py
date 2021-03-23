from vkwave.bots import Keyboard


def student_card():
    kb = Keyboard()

    kb.add_text_button(
        "Контакты",
        payload={"button": "get_contacts"},
    )
    kb.add_text_button(
        "Редактировать",
        payload={"button": "edit_student"},
    )
    kb.add_row()
    kb.add_text_button("◀️ Назад", payload={"button": "main_menu"})

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
    kb.add_text_button("◀️ Назад", payload={"button": "main_menu"})

    return kb.get_keyboard()
