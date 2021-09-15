from vkbottle import Keyboard, Text

from jacob.database.utils.universities import get_universities


async def list_of_universities():
    kb = Keyboard()
    # FIXME: Клавиатура не должна пинать базу данных, вытащить в аргумент
    for university in await get_universities():
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
