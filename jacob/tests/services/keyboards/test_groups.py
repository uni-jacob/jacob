import json

import pytest


@pytest.mark.asyncio
async def test_managed_groups():
    from jacob.database.utils.groups import get_managed_groups
    from jacob.services.keyboards import managed_groups

    groups = await get_managed_groups(549350532)
    keyboard = managed_groups(groups)

    assert json.loads(keyboard) == {
        "buttons": [
            [
                {
                    "action": {
                        "label": "✅ ИСТ-220@ВГУ",
                        "payload": {
                            "action": "select",
                            "block": "groups",
                            "group_id": 16,
                        },
                        "type": "text",
                    }
                },
                {
                    "action": {
                        "label": "✅ ИСТ-120@ВГУ",
                        "payload": {
                            "action": "select",
                            "block": "groups",
                            "group_id": 15,
                        },
                        "type": "text",
                    }
                },
            ],
            [
                {
                    "action": {
                        "label": "Создать новую группу",
                        "payload": {"action": "init", "block": "registration"},
                        "type": "text",
                    }
                },
                {
                    "action": {
                        "label": "Сохранить",
                        "payload": {"block": "main_menu"},
                        "type": "text",
                    }
                },
            ],
        ],
        "inline": False,
        "one_time": False,
    }
