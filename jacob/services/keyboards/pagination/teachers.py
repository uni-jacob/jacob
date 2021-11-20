from vkbottle import Text

from jacob.services.keyboards.pagination.alphabet import (
    AbstractPersonalitiesPagination,
)


class TeachersPagination(AbstractPersonalitiesPagination):
    def function_menu(self) -> str:
        kb = self._halves
        kb.row()
        kb.add(
            Text(
                "Создать преподавателя",
                {"block": "schedule", "action": "create:teacher"},
            ),
        )
        kb.row()
        kb.add(
            Text(
                "Назад",
                {"block": "schedule", "action": "select:lesson"},
            ),
        )
        return kb.get_json()

    def submenu(self, half_ind: int) -> str:
        kb = self._get_letters_in_half(half_ind)
        kb.row()
        kb.add(
            Text(
                "Назад",
                {"block": "schedule", "action": "select:lesson_type"},
            ),
        )
        return kb.get_json()

    def entries_menu(self, letter: str) -> str:
        half_ind = self._find_half_index_of_letter(letter)
        kb = self._get_personalities_in_letter(letter)
        kb.row()
        kb.add(
            Text(
                "Назад",
                {
                    "block": "schedule",
                    "action": "half",
                    "half": half_ind,
                },
            ),
        )
        return kb.get_json()
