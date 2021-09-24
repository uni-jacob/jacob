from abc import ABC, abstractmethod
from typing import Optional, Tuple, Union

from vkbottle import Keyboard, Text

from jacob.database import models


class ABCPersonalitiesPagination(ABC):
    def __init__(self, source: list[models.Personality], block: str = ""):
        self.source = source
        self.block = block

    def _generate_list_of_letters(self) -> list[str]:
        return [personality.last_name[0] for personality in self.source]

    def _get_alphabet_ranges(
        self,
    ) -> Union[Tuple, Tuple[list[str]]]:
        alphabet = self._generate_list_of_letters()
        ranges_len = len(alphabet) // 2
        ranges = (alphabet[:ranges_len], alphabet[ranges_len:])
        if not any(ranges):
            return ()
        if not all(ranges):
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
                    {
                        "block": self.block,
                        "action": "half",
                        "half": index,
                    },
                ),
            )

        return kb

    def _get_letters_in_half(self, half_ind: int) -> Keyboard:
        kb = Keyboard()
        halves = self._get_alphabet_ranges()
        for letter in halves[half_ind]:
            kb.add(
                Text(
                    letter,
                    {"block": self.block, "action": "select_letter", "letter": letter},
                ),
            )
            if len(kb.buttons) == 5:
                kb.row()

        return kb

    def _get_personalities_in_letter(self, letter: str) -> Keyboard:
        kb = Keyboard()
        for personality in self.source:
            if personality.last_name.startswith(letter):
                kb.add(
                    Text(
                        f"{personality.first_name} {personality.last_name}",
                        {
                            "block": self.block,
                            "action": "select_personality",
                            "personality_id": personality.id,
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
    def submenu(self, half_ind: int) -> str:
        """Подменю функции (список букв в половине алфавита). Имплементируется в подклассах конкретных функций.

        Args:
            half_ind: ИД половины алфавита

        Returns:
            str: Клавиатура
        """
        pass

    @abstractmethod
    def entries_menu(self, letter: str) -> str:
        """Меню элементов списка. Имплементируется в подклассах конкретных функций.

        Args:
            letter: Буква

        Returns:
            str: Клавиатура
        """
        pass
