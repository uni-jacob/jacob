import json

from jacob.services.keyboards import schedule_main


def test_schedule_main_if_is_admin():
    keyboard = schedule_main(True)
    assert json.loads(keyboard) == {
        "buttons": [
            [
                {
                    "action": {
                        "label": "Редактировать",
                        "payload": {"action": "edit", "block": "schedule"},
                        "type": "text",
                    }
                },
                {
                    "action": {
                        "label": "Просмотреть",
                        "payload": {"action": "view", "block": "schedule"},
                        "type": "text",
                    }
                },
            ],
            [
                {
                    "action": {
                        "label": "Назад",
                        "payload": {"block": "main_menu"},
                        "type": "text",
                    }
                }
            ],
        ],
        "inline": False,
        "one_time": False,
    }


def test_schedule_main_if_is_not_admin():
    keyboard = schedule_main(True)
    assert json.loads(keyboard) == {
        "buttons": [
            [
                {
                    "action": {
                        "label": "Просмотреть",
                        "payload": {"action": "view", "block": "schedule"},
                        "type": "text",
                    }
                },
            ],
            [
                {
                    "action": {
                        "label": "Назад",
                        "payload": {"block": "main_menu"},
                        "type": "text",
                    }
                }
            ],
        ],
        "inline": False,
        "one_time": False,
    }
