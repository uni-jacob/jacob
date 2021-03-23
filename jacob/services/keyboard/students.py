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
