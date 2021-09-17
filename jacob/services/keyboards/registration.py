from vkbottle import Keyboard, Text

from jacob.database import models


async def list_of_universities(universities: list[models.University]) -> str:
    kb = Keyboard()
    for university in universities:
        if len(kb.buttons) == 4:
            kb.row()
        kb.add(
            Text(
                university.abbreviation,
                {
                    "block": "registration",
                    "action": "university:select",
                    "university": university.id,
                },
            )
        )
    kb.row()
    kb.add(Text("Создать", {"block": "registration", "action": "university:create"}))
    kb.add(
        Text(
            "Назад",
            {"block": "main_menu"},
        )
    )
    return kb.get_json()
