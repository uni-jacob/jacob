from vkwave.bots import Keyboard


def group_menu():
    kb = Keyboard()
    kb.add_text_button(
        "Студенты",
        payload={"button": "students"},
    )
    kb.add_row()
    kb.add_text_button(
        text="◀️ Назад",
        payload={"button": "main_menu"},
    )

    return kb.get_keyboard()
