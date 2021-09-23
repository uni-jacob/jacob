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

    Args:
        source: Список объектов типов недель.

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


def days(source: list[models.DayOfWeek]) -> str:
    """
    Клавиатура со списком доступных дней недели.

    Args:
        source: Список объектов дней недели.

    Returns:
        str: Клавиатура
    """
    kb = Keyboard()
    for day in source:
        kb.add(
            Text(
                day.name,
                {
                    "block": "schedule",
                    "action": "select:day",
                    "day": day.id,
                },
            ),
        )
        if len(kb.buttons[-1]) == 3:
            kb.row()
    kb.row()
    kb.add(Text("Назад", {"block": "schedule", "action": "edit"}))

    return kb.get_json()


def timetable(source: list[models.Timetable]) -> str:
    """
    Клавиатура со списком доступных пар.

    Args:
        source: Список объектов пар.

    Returns:
        str: Клавиатура
    """
    kb = Keyboard()
    for lesson_time in source:
        kb.add(
            Text(
                f"{lesson_time.start_time} - {lesson_time.end_time}",
                {
                    "block": "schedule",
                    "action": "select:lesson",
                    "day": lesson_time.id,
                },
            ),
        )
        if len(kb.buttons[-1]) == 3:
            kb.row()
    kb.row()
    kb.add(
        Text("Создать время занятия", {"block": "schedule", "action": "create:time"})
    )
    kb.row()
    kb.add(Text("Назад", {"block": "schedule", "action": "select:week"}))

    return kb.get_json()
