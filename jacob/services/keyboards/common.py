from vkbottle import Keyboard, Text, KeyboardButtonColor


def cancel() -> str:
    """Создаёт универсальную клавиатуру с кнопкой "Отмена"."""
    kb = Keyboard()
    kb.add(Text("Отмена", {"action": "cancel"}), color=KeyboardButtonColor.NEGATIVE)

    return kb.get_json()
