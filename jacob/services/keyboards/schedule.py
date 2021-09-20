from vkbottle import Keyboard, Text


def schedule_main() -> str:
    """
    Главное меню расписания

    Returns:
        str: Клавиатура с главным меню
    """
    kb = Keyboard()
    kb.add(Text("Редактировать", {"block": "schedule", "action": "edit"}))
    kb.add(Text("Просмотреть", {"block": "schedule", "action": "view"}))
    kb.row()
    kb.add(Text("Назад", {"block": "main_menu"}))
    return kb.get_json()
