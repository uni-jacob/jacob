import os
import typing as t
from abc import ABC
from abc import abstractmethod

from pony import orm
from vkwave.api import API
from vkwave.bots import Keyboard
from vkwave.client import AIOHTTPClient

from jacob.database.utils import admin, chats, students, groups, lists
from jacob.database.utils.storages import managers
from jacob.services import chats as chat_utils

JSONStr = str
api_session = API(tokens=os.getenv("VK_TOKEN"), clients=AIOHTTPClient())
api = api_session.get_context()


class Keyboards(ABC):
    """Базовая клавиатура-навигатор между экранами выбора студентов."""

    @abstractmethod
    def __init__(self, admin_id: int):
        """
        Создание новой клавиатуры.

        Args:
            admin_id: Идентификатор администратора
        """
        self.admin_id = admin_id
        self.return_to = ""

    @abstractmethod
    def menu(self) -> str:
        """Главное меню функции, реализуется в подклассах."""
        pass

    @abstractmethod
    def submenu(self, half: int) -> str:
        alphabet = students.get_unique_second_name_letters_in_a_group(
            admin.get_active_group(self.admin_id),
        )
        half_len = len(alphabet) // 2
        halfs = alphabet[:half_len], alphabet[half_len:]

        kb = Keyboard()

        for letter in halfs[half]:
            if len(kb.buttons[-1]) == 4:
                kb.add_row()
            kb.add_text_button(letter, payload={"button": "letter", "value": letter})
        if kb.buttons[-1]:
            kb.add_row()
        kb.add_text_button("◀️ Назад", payload={"button": self.return_to})

        return kb.get_keyboard()

    @orm.db_session
    @abstractmethod
    def students(self, letter: str) -> str:
        data = students.get_list_of_students_by_letter(self.admin_id, letter)
        selected = managers.MentionStorageManager(
            self.admin_id
        ).get_mentioned_students()
        half_index = self._find_half_index_of_letter(letter)
        kb = Keyboard()
        for item in data:
            if len(kb.buttons[-1]) == 2:
                kb.add_row()
            label = " "
            if item.id in selected:
                label = "✅ "
            kb.add_text_button(
                text=f"{label}{item.last_name} {item.first_name}",
                payload={
                    "button": "student",
                    "student_id": item.id,
                    "letter": letter,
                    "name": f"{item.last_name} {item.first_name}",
                },
            )
        if kb.buttons[-1]:
            kb.add_row()
        kb.add_text_button(
            text="◀️ Назад",
            payload={"button": "half", "half": half_index},
        )

        return kb.get_keyboard()

    def _get_halfs_of_alphabet(self) -> t.Tuple[t.List[str]]:
        """
        Создает половины алфавита из списка студентов.

        Returns:
            t.Tuple[t.List[str]]: Половины алфавита
        """
        alphabet = students.get_unique_second_name_letters_in_a_group(
            admin.get_active_group(self.admin_id),
        )
        half_len = len(alphabet) // 2

        return alphabet[:half_len], alphabet[half_len:]

    def _find_half_index_of_letter(self, letter: str) -> int:
        """
        Определяет в какой половине алфавита находится буква и возвращает ее индекс.

        Args:
            letter: Буква для проверки

        Returns:
            int: Индекс половины
        """
        halfs = self._get_halfs_of_alphabet()

        for index, half in enumerate(halfs):
            if letter in half:
                return index


class StudentsNavigator(ABC):
    """Базовый конструктор клавиатур-навигаторов между экранами выбора студентов."""

    @abstractmethod
    def __init__(self, admin_id: int):
        self.admin_id = admin_id

    @abstractmethod
    def render(self) -> Keyboards:
        return Keyboards(self.admin_id)


def alphabet(admin_id: int) -> Keyboard:
    """
    Генерирует фрагмент клавиатуры с половинами алфавита фамилиий студентов.

    Args:
        admin_id: Идентификатор администратора

    Returns:
        Keyboard: Фрагмент клавиатуры
    """
    kb = Keyboard()
    alphabet = students.get_unique_second_name_letters_in_a_group(
        admin.get_active_group(admin_id),
    )
    half_len = len(alphabet) // 2
    f_alphabet, s_alphabet = alphabet[:half_len], alphabet[half_len:]
    index = 0
    for half in f_alphabet, s_alphabet:
        if half[0] == half[-1]:
            title = f"{half[0]}"
        else:
            title = f"{half[0]}..{half[-1]}"
        kb.add_text_button(title, payload={"button": "half", "half": index})
        index += 1

    return kb


async def list_of_chats(api_context, admin_id: int):
    """
    Генерирует фрагмент клавиатуры со списком подключенных чатов.

    Args:
        api_context: Объект API ВК.
        admin_id: идентификатор пользователя

    Returns:
        Keyboard: Фрагмент клавиатуры
    """
    kb = Keyboard()
    with orm.db_session:
        chat_objects = chats.get_list_of_chats_by_group(
            admin.get_active_group(admin_id),
        )
        for chat in chat_objects:
            chat_title = await chat_utils.get_chat_name(
                api_context,
                chat.vk_id,
            )
            kb.add_text_button(
                chat_title,
                payload={
                    "button": "chat",
                    "chat_id": chat.id,
                },
            )
    return kb


def prompt() -> Keyboard:
    """
    Генерирует клавиатуру с подтверждением действия.

    Returns:
        Keyboard: Объект клавиатуры
    """
    kb = Keyboard()
    kb.add_text_button(text="✅ Подтвердить", payload={"button": "confirm"})
    kb.add_text_button(text="🚫 Отменить", payload={"button": "deny"})
    return kb


def empty() -> JSONStr:
    kb = Keyboard()

    return kb.get_empty_keyboard()


def cancel() -> Keyboard:
    """
    Генерирует клавиатуру для отмены действия.

    Returns:
        JSONStr: клавиатура
    """
    kb = Keyboard()

    kb.add_text_button("🚫 Отмена", payload={"button": "cancel"})

    return kb


def confirm_with_chat_update():

    kb = prompt()

    if kb.buttons[-1]:
        kb.add_row()

    chat_emoji = "📡"
    kb.add_text_button(
        text=f"{chat_emoji} Переключить чат",
        payload={"button": "chat_config"},
    )

    return kb.get_keyboard()


def cancel_with_cleanup():
    kb = cancel()

    kb.add_row()
    kb.add_text_button("Очистить", payload={"button": "edit_cleanup"})

    return kb.get_keyboard()


def subgroups(group_id: int):
    kb = Keyboard()

    request = list(filter(bool, groups.get_subgroups_in_group(group_id)))

    for subgroup in request:
        if len(kb.buttons[-1]) == 2:
            kb.add_row()
        kb.add_text_button(
            subgroup, payload={"button": "subgroup", "subgroup": subgroup}
        )

    if kb.buttons[-1]:
        kb.add_row()
    kb.add_text_button(text="◀️ Назад", payload={"button": "presets"})

    return kb.get_keyboard()


def academic_statuses(group_id: int):
    kb = Keyboard()

    request = list(filter(bool, groups.get_academic_statuses_in_group(group_id)))

    for ac in request:
        if len(kb.buttons[-1]) == 2:
            kb.add_row()
        kb.add_text_button(
            ac.description, payload={"button": "ac_status", "status": ac.id}
        )

    if kb.buttons[-1]:
        kb.add_row()

    kb.add_text_button(text="◀️ Назад", payload={"button": "presets"})

    return kb.get_keyboard()


def custom_presets(group_id: int):
    kb = Keyboard()

    request = lists.get_lists_of_group(group_id)

    with orm.db_session:
        for preset in request:
            if len(kb.buttons[-1]) == 2:
                kb.add_row()
            kb.add_text_button(
                preset.name, payload={"button": "preset", "preset": preset.id}
            )

    if kb.buttons[-1]:
        kb.add_row()

    kb.add_text_button(text="◀️ Назад", payload={"button": "presets"})

    return kb.get_keyboard()
