from vkbottle import Keyboard, Text


def register_start() -> str:
    kb = Keyboard(inline=True)
    kb.add(Text("Регистрация", payload={"block": "registration", "action": "init"}))

    return kb.get_json()
