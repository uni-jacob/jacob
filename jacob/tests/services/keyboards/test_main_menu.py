import json

from jacob.services.keyboards import main_menu, register_start


def test_register_start():
    keyboard = register_start()
    assert json.loads(keyboard) == {
        "buttons": [
            [
                {
                    "action": {
                        "label": "Регистрация",
                        "payload": {"action": "init", "block": "registration"},
                        "type": "text",
                    }
                }
            ]
        ],
        "inline": True,
        "one_time": False,
    }


class TestMainMenu:
    def test_main_menu_with_admin(self):
        keyboard = main_menu(True)
        assert json.loads(keyboard) == {
            "buttons": [
                [
                    {
                        "action": {
                            "label": "Расписание",
                            "payload": {"action": "init", "block": "schedule"},
                            "type": "text",
                        }
                    }
                ],
                [
                    {
                        "action": {
                            "label": "Назад к группам",
                            "payload": {"action": "show", "block": "groups"},
                            "type": "text",
                        }
                    }
                ],
            ],
            "inline": False,
            "one_time": False,
        }

    def test_main_menu_with_non_admin(self):
        keyboard = main_menu(False)
        assert json.loads(keyboard) == {
            "buttons": [],
            "inline": False,
            "one_time": False,
        }
