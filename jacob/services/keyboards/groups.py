from vkbottle import Keyboard, Text

from jacob.database import models


async def managed_groups(entries: list[models.Admin]) -> str:
    """
    Генерирует клавиатуру со списком доступных для модерации групп

    Args:
        entries: Список модерируемых групп
    Returns:
        str: Клавиатура

    """
    kb = Keyboard()

    for entry in entries:
        if len(kb.buttons) == 2:
            kb.row()
        selected = "✅ " if entry.is_active else ""
        group = await entry.group
        university = await group.university
        kb.add(Text(f"{selected}{group.group_number}@{university.abbreviation}"))

    kb.row()
    kb.add(Text("Создать новую группу", {"block": "registration", "action": "init"}))
    kb.add(Text("Сохранить", {"block": "main_menu"}))

    return kb.get_json()
