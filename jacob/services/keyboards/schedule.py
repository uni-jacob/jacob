from vkbottle import Keyboard, Text

from jacob.database import models


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


def weeks(source: list[models.Week]) -> str:
    """
    Клавиатура со списком доступных недель.

    Returns:
        str: Клавиатура
    """
    kb = Keyboard()
    for week in source:
        if len(kb.buttons) == 2:
            kb.row()
        kb.add(
            Text(
                week.name,
                {
                    "block": "schedule",
                    "action": "select:week",
                    "week": week.id,
                },
            ),
        )
    kb.row()
    kb.add(Text("Назад", {"block": "schedule", "action": "init"}))

    return kb.get_json()