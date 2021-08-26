from vkbottle import Keyboard, Text

from jacob.database.utils.universities import get_universities


async def list_of_universities():
    kb = Keyboard()
    for university in await get_universities():
        kb.add(
            Text(
                university.name,
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
            {"block": "registration", "action": "registration:select_university"},
        )
    )
    return kb.get_json()
