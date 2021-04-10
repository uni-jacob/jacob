from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from vkwave.bots import Keyboard

from jacob.database import models

JSONStr = str


class Navigator(ABC):
    def __init__(self, owner: int):
        self.owner: int = owner

    @abstractmethod
    def _get_alphabet(self) -> List[str]:
        """Получает список первых букв фамилий активной группы.

        Должен быть реализован в дочерних классах.

        Returns:
            Optional[List[str]]: список букв
        """
        ...

    @abstractmethod
    def _get_students_by_letter(self, letter: str) -> Optional[List[models.Student]]:
        """Получает список студентов по первой букве фамилии.

        Должен быть реализован в дочерних классах.

        Args:
            letter: первая буква фамилии

        Returns:
            Optional[List[models.Student]]: список студентов
        """
        ...

    def _halves_of_alphabet(self):
        kb = Keyboard()

        f_alphabet, s_alphabet = self._get_halves()
        for index, half in enumerate([f_alphabet, s_alphabet]):
            if half[0] == half[-1]:
                title = f"{half[0]}"
            else:
                title = f"{half[0]}..{half[-1]}"
            kb.add_text_button(title, payload={"button": "half", "half": index})

        return kb

    def _half_of_alphabet(self, half: int):
        kb = Keyboard()

        halves = self._get_halves()

        for letter in halves[half]:
            if len(kb.buttons[-1]) == 4:
                kb.add_row()
            kb.add_text_button(letter, payload={"button": "letter", "value": letter})

        if kb.buttons[-1]:
            kb.add_row()

        return kb

    def _get_halves(self) -> Tuple[List[str], List[str]]:
        alphabet = self._get_alphabet()

        pivot = len(alphabet) // 2

        return alphabet[:pivot], alphabet[pivot:]

    def _find_half_index_of_letter(self, letter: str) -> Optional[int]:
        halves = self._get_halves()

        saved_index = None

        for index, half in enumerate(halves):
            if letter in half:
                saved_index = index
                break

        return saved_index

    @abstractmethod
    def menu(self) -> JSONStr:
        """Генерирует готовое меню функции.

        Должен быть реализован в дочерних классах.

        Returns:
             JSONStr: готовая клавиатура
        """
        ...

    @abstractmethod
    def submenu(self, half: int) -> JSONStr:
        """Генерирует подменю функции (список букв алфавита в половине).

        Должен быть реализован в дочерних классах.

        Args:
            half: индекс половины алфавита

        Returns:
            JSONStr: готовая клавиатура
        """
        ...

    @abstractmethod
    def students(self, letter: str) -> JSONStr:
        """Генерирует список студентов, чьи фамилии начинаются на букву.

        Должен быть реализован в дочерних классах.

        Args:
            letter: первая буква фамилии

        Returns:
            JSONStr: готовая клавиатура
        """
        ...
