import json


def test_cancel():
    from jacob.services.keyboards import cancel

    keyboard = cancel()

    assert json.loads(keyboard) == {
        "one_time": False,
        "inline": False,
        "buttons": [
            [
                {
                    "action": {
                        "label": "\u041e\u0442\u043c\u0435\u043d\u0430",
                        "payload": {"action": "cancel"},
                        "type": "text",
                    },
                    "color": "negative",
                }
            ]
        ],
    }


def test_yes_no():
    from jacob.services.keyboards import yes_no

    keyboard = yes_no()

    assert json.loads(keyboard) == {
        "one_time": False,
        "inline": False,
        "buttons": [
            [
                {
                    "action": {
                        "label": "\u0414\u0430",
                        "payload": {"action": "yes"},
                        "type": "text",
                    },
                    "color": "positive",
                },
                {
                    "action": {
                        "label": "\u041d\u0435\u0442",
                        "payload": {"action": "no"},
                        "type": "text",
                    },
                    "color": "negative",
                },
            ]
        ],
    }
