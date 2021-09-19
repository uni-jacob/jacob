import json

import pytest

from jacob.database.utils.students import get_students_in_group
from jacob.services.keyboards.pagination.alphabet import ABCStudentsPagination


@pytest.fixture
async def pagination():
    source = await get_students_in_group(15)

    ABCStudentsPagination.__abstractmethods__ = set()
    return ABCStudentsPagination(source)


class TestHalvesKeyboard:
    def test__generate_list_of_letters(self, pagination):
        assert pagination._generate_list_of_letters() == ["Г"]

    def test__get_alphabet_ranges(self, pagination):
        # TODO: добавить группу с несколькими студентами и тест этого метода для неё
        assert pagination._get_alphabet_ranges() == (["Г"],)

    def test__find_half_index_of_letter_if_letter_exists(self, pagination):
        assert pagination._find_half_index_of_letter("Г") == 0

    def test__find_half_index_of_letter_if_letter_not_exists(self, pagination):
        assert pagination._find_half_index_of_letter("Д") is None

    @pytest.mark.asyncio
    async def test__halves(self, pagination):
        assert json.loads(pagination._halves().get_json()) == {
            "buttons": [
                [
                    {
                        "action": {
                            "label": "Г",
                            "payload": {
                                "action": "half",
                                "block": "pagination:students",
                                "half": 0,
                            },
                            "type": "text",
                        }
                    }
                ]
            ],
            "inline": False,
            "one_time": False,
        }

    def test__get_letters_in_half(self, pagination):
        assert json.loads(pagination._get_letters_in_half(0).get_json()) == {
            "buttons": [
                [
                    {
                        "action": {
                            "label": "Г",
                            "payload": {
                                "action": "select_letter",
                                "block": "",
                                "letter": "Г",
                            },
                            "type": "text",
                        }
                    }
                ]
            ],
            "inline": False,
            "one_time": False,
        }

    def test__get_students_in_letter(self, pagination):
        assert json.loads(pagination._get_students_in_letter("Г").get_json()) == {
            "buttons": [
                [
                    {
                        "action": {
                            "label": "Даниил Голубев",
                            "payload": {
                                "action": "select_student",
                                "block": "",
                                "student_id": 7,
                            },
                            "type": "text",
                        }
                    }
                ]
            ],
            "inline": False,
            "one_time": False,
        }
