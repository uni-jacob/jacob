from vkbottle import Keyboard, Text


def register_start() -> str:
    kb = Keyboard(inline=True)
    kb.add(Text("Регистрация", payload={"block": "registration", "action": "init"}))

    return kb.get_json()


def main_menu(is_admin: bool) -> str:
    kb = Keyboard()

    if is_admin:
        kb.add(Text("Расписание", payload={"block": "schedule", "action": "init"}))

    return kb.get_json()
