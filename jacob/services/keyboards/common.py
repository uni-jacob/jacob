from vkbottle import Keyboard, KeyboardButtonColor, Text


def cancel() -> str:
    """Создаёт универсальную клавиатуру с кнопкой "Отмена"."""
    kb = Keyboard()
    kb.add(Text("Отмена", {"action": "cancel"}), color=KeyboardButtonColor.NEGATIVE)

    return kb.get_json()


def yes_no() -> str:
    """Создаёт универсальную клавиатуру с кнопками "Да"/"Нет"."""
    kb = Keyboard()
    kb.add(Text("Да", {"action": "yes"}), color=KeyboardButtonColor.POSITIVE)
    kb.add(Text("Нет", {"action": "no"}), color=KeyboardButtonColor.NEGATIVE)

    return kb.get_json()
