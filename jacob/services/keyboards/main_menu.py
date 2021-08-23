from vkbottle import Keyboard, Text


def register_or_invite() -> str:
    kb = Keyboard()
    kb.add(Text("Регистрация", payload={"block": "registration", "action": "init"}))
    kb.add(
        Text(
            "У меня есть код",
            payload={"block": "registration", "action": "enter_invite"},
        ),
    )

    return kb.get_json()
