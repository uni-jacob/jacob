from vkbottle import Keyboard, Text

from jacob.database import models


def managed_groups(entries: list[models.Admin]) -> str:
    """
    Генерирует клавиатуру со списком доступных для модерации групп

    Args:
        entries: Список модерируемых групп

    Returns:
        str: Клавиатура

    """
    kb = Keyboard()

    for entry in entries:
        selected = "✅ " if entry.is_active else ""
        kb.add(
            Text(
                f"{selected}{entry.group.group_number}@{entry.group.university.abbreviation}",
                {
                    "block": "groups",
                    "action": "select",
                    "group_id": entry.group.id,
                },
            ),
        )
        if len(kb.buttons[-1]) == 2:
            kb.row()

    if kb.buttons[-1]:
        kb.row()
    kb.add(Text("Создать новую группу", {"block": "registration", "action": "init"}))
    kb.add(Text("Сохранить", {"block": "main_menu"}))

    return kb.get_json()
