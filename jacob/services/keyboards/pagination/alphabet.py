from abc import ABC, abstractmethod
from typing import Optional, Tuple, Union

from vkbottle import Keyboard, Text

from jacob.database import models


class ABCStudentsPagination(ABC):
    def __init__(self, source: list[models.Student]):
        self.source = source
        self.block = ""

    def _generate_list_of_letters(self) -> list[str]:
        return [student.last_name[0] for student in self.source]

    def _get_alphabet_ranges(
        self,
    ) -> Union[Tuple[list[str], list[str]], Tuple[list[str]]]:
        alphabet = self._generate_list_of_letters()
        ranges_len = len(alphabet) // 2
        if not all((alphabet[:ranges_len], alphabet[ranges_len:])):
            return (alphabet[:ranges_len] or alphabet[ranges_len:],)
        return alphabet[ranges_len:], alphabet[:ranges_len]

    def _find_half_index_of_letter(self, letter: str) -> Optional[int]:
        for index, half in enumerate(self._get_alphabet_ranges()):
            if letter in half:
                return index

    def _halves(self) -> Keyboard:
        kb = Keyboard()
        for index, half in enumerate(self._get_alphabet_ranges()):
            if half[0] == half[-1]:
                title = half[0]
            else:
                title = f"{half[0]}..{half[-1]}"
            kb.add(
                Text(
                    title,
                    {"block": "pagination:students", "action": "half", "half": index},
                ),
            )

        return kb

    def _get_letters_in_half(self, half_ind: int) -> Keyboard:
        kb = Keyboard()
        halves = self._get_alphabet_ranges()
        for letter in halves[half_ind]:
            if len(kb.buttons) == 5:
                kb.row()
            kb.add(
                Text(
                    letter,
                    {"block": self.block, "action": "select_letter", "letter": letter},
                ),
            )

        return kb

    def _get_students_in_letter(self, letter: str) -> Keyboard:
        kb = Keyboard()
        for student in self.source:
            if student.last_name.startswith(letter):
                kb.add(
                    Text(
                        f"{student.first_name} {student.last_name}",
                        {
                            "block": self.block,
                            "action": "select_student",
                            "student_id": student.id,
                        },
                    ),
                )
            if len(kb.buttons[-1]) == 2:
                kb.row()
        return kb

    @abstractmethod
    def function_menu(self) -> str:
        """Меню функции. Имплементируется в подклассах конкретных функций"""
        pass

    @abstractmethod
    def submenu(self) -> str:
        """Подменю функции (список букв в половине алфавита). Имплементируется в подклассах конкретных функций."""
        pass

    @abstractmethod
    def entries_menu(self) -> str:
        """Меню элементов списка. Имплементируется в подклассах конкретных функций."""
        pass
