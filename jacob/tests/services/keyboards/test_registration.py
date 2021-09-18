import json

import pytest

from jacob.database.utils.universities import get_universities
from jacob.services.keyboards import list_of_universities


@pytest.mark.asyncio
async def test_list_of_universities():
    universities = await get_universities()
    keyboard = await list_of_universities(universities)
    assert json.loads(keyboard) == {
        "buttons": [
            [
                {
                    "action": {
                        "label": "ВГУ",
                        "payload": {
                            "action": "university:select",
                            "block": "registration",
                            "university": 28,
                        },
                        "type": "text",
                    }
                }
            ],
            [
                {
                    "action": {
                        "label": "Создать",
                        "payload": {
                            "action": "university:create",
                            "block": "registration",
                        },
                        "type": "text",
                    }
                },
                {
                    "action": {
                        "label": "Назад",
                        "payload": {"block": "main_menu"},
                        "type": "text",
                    }
                },
            ],
        ],
        "inline": False,
        "one_time": False,
    }
