from vkbottle import Keyboard, Text

from jacob.database import models


async def list_of_universities(universities: list[models.University]) -> str:
    """
    Генерирует клавитуру со списком зарегистрированных университетов.

    Args:
        universities: Список университетов

    Returns:
        str: JSON клавиатуры
    """
    kb = Keyboard()
    for university in universities:
        if len(kb.buttons) == 4:
            kb.row()
        kb.add(
            Text(
                university.abbreviation or university.name,
                {
                    "block": "registration",
                    "action": "university:select",
                    "university": university.id,
                },
            ),
        )
    kb.row()
    kb.add(Text("Создать", {"block": "registration", "action": "university:create"}))
    kb.add(
        Text(
            "Назад",
            {"block": "main_menu"},
        ),
    )
    return kb.get_json()
