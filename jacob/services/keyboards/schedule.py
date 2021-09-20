from vkbottle import Keyboard, Text


def schedule_main(is_admin: bool) -> str:
    """
    Главное меню расписания

    Args:
        is_admin: Пользователь администратор?

    Returns:
        str: Клавиатура с главным меню
    """
    kb = Keyboard()

    if is_admin:
        kb.add(Text("Редактировать", {"block": "schedule", "action": "edit"}))

    kb.add(Text("Просмотреть", {"block": "schedule", "action": "view"}))
    kb.row()
    kb.add(Text("Назад", {"block": "main_menu"}))
    return kb.get_json()
