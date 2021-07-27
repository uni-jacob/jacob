from vkbottle import Callback, Keyboard


def register_or_invite() -> str:
    kb = Keyboard()
    kb.add(Callback("Регистрация", payload={"block": "registration", "action": "init"}))
    kb.add(
        Callback(
            "У меня есть код",
            payload={"block": "registration", "action": "enter_invite"},
        ),
    )

    return kb.get_json()
