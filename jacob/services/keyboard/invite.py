from vkwave.bots import Keyboard


def add_request_confirm(user_id: int):
    kb = Keyboard()
    kb.add_text_button("Добавить", payload={"button": "invite_user", "user": user_id})
    kb.add_text_button("Отклонить", payload={"button": "decline_user", "user": user_id})
    return kb.get_keyboard()
