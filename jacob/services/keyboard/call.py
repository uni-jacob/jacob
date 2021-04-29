from typing import List

from pony import orm
from vkwave.bots import Keyboard

from jacob.database import redis
from jacob.database.utils import admin, students
from jacob.database.utils.storages import managers
from jacob.services import keyboard as kbs
from jacob.services.keyboard.common import Keyboards, StudentsNavigator

JSONStr = str


class CallKeyboards(Keyboards):
    """Набор клавиатур для навигации в режиме Призыва."""

    def __init__(self, admin_id: int, return_to: str):
        super().__init__(admin_id)
        self.return_to = return_to

    @orm.db_session
    def menu(self, group_ids: List[int]) -> str:
        """
        Главное меню призыва (половины алфавита, сохранить, отменить, изменить).

        Args:
            group_ids: Список идентификаторов групп

        Returns:
            str: Клавиатура
        """
        kb = kbs.common.alphabet(group_ids)
        if len(kb.buttons[-1]):
            kb.add_row()
        kb.add_text_button(text="✅ Сохранить", payload={"button": "save_selected"})
        kb.add_text_button(text="📜 Пресеты", payload={"button": "presets"})
        kb.add_row()
        kb.add_text_button(text="✏️ Изменить текст", payload={"button": "call"})
        if len(admin.get_admin_feud(self.admin_id)) > 1:
            kb.add_text_button(
                "Выбрать группы",
                payload={"button": "mention_select_groups"},
            )
        kb.add_row()
        kb.add_text_button(text="🚫 Отмена", payload={"button": "cancel_call"})

        return kb.get_keyboard()

    async def submenu(self, half: int) -> str:
        """
        Подменю призыва (список букв в рамках половины алфавита).

        Args:
            half: Индекс половины алфавита

        Returns:
            str: Клавиатура

        """
        group_ids: List[int] = list(
            map(
                int,
                await redis.lget(
                    "mention_selected_groups:{0}".format(self.admin_id),
                ),
            ),
        )
        if not group_ids:
            group_ids = [admin.get_active_group(self.admin_id).id]
        alphabet = students.get_unique_second_name_letters_in_a_group(
            group_ids,
        )
        half_len = len(alphabet) // 2
        halves = alphabet[:half_len], alphabet[half_len:]

        kb = Keyboard()

        for letter in halves[half]:
            if len(kb.buttons[-1]) == 4:
                kb.add_row()
            kb.add_text_button(letter, payload={"button": "letter", "value": letter})
        if kb.buttons[-1]:
            kb.add_row()
        kb.add_text_button("◀️ Назад", payload={"button": self.return_to})

        return kb.get_keyboard()

    @orm.db_session
    def students(self, group_ids: List[int], letter: str) -> str:
        """
        Список студентов на букву.

        Args:
            group_ids: Идентификаторы групп
            letter: Первая буква фамилии для поиска студентов

        Returns:
            str: Клавиатура

        """
        data = students.get_list_of_students_by_letter(group_ids, letter)
        selected = managers.MentionStorageManager(
            self.admin_id,
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


class CallNavigator(StudentsNavigator):
    def __init__(self, admin_id: int):
        super().__init__(admin_id)
        self.return_to = "skip_call_message"

    def render(self):
        return CallKeyboards(self.admin_id, self.return_to)


def skip_call_message() -> JSONStr:
    """
    Генерирует клавиатуру для пропуска ввода сообщения призыва.

    Returns:
        JSONStr: Строка с клавиатурой
    """
    kb = Keyboard()
    kb.add_text_button(text="⏩ Пропустить", payload={"button": "skip_call_message"})

    kb.add_text_button(text="🚫 Отмена", payload={"button": "cancel_call"})
    return kb.get_keyboard()


def call_prompt(admin_id: int) -> JSONStr:
    """
    Генерирует клавиатуру с настройкой призыва.

    Args:
        admin_id: идентификатор администратора

    Returns:
        JSONStr:  Клавиатура
    """
    kb = kbs.common.prompt()
    kb.add_row()
    store = managers.AdminConfigManager(admin_id)
    if store.get_names_usage():
        names_emoji = "✅"
    else:
        names_emoji = "🚫"
    chat_emoji = "📡"
    kb.add_text_button(text="◀️ Назад", payload={"button": "skip_call_message"})
    kb.add_row()
    kb.add_text_button(
        text=f"{names_emoji} Использовать имена",
        payload={"button": "names_usage"},
    )
    kb.add_text_button(
        text=f"{chat_emoji} Переключить чат",
        payload={"button": "chat_config"},
    )
    return kb.get_keyboard()


def presets():
    kb = Keyboard()

    kb.add_text_button(text="Все студенты", payload={"button": "call_all"})
    kb.add_text_button("Подгруппы", payload={"button": "subgroups"})
    kb.add_row()
    kb.add_text_button("Формы обучения", payload={"button": "academic_statuses"})
    kb.add_row()
    kb.add_text_button("Пользовательские пресеты", payload={"button": "custom_presets"})
    kb.add_row()
    kb.add_text_button(text="◀️ Назад", payload={"button": "skip_call_message"})

    return kb.get_keyboard()


@orm.db_session
def list_of_groups(admin_id: int, selected: List[int]):
    kb = Keyboard()

    groups = admin.get_admin_feud(admin_id)

    for group in groups:
        if len(kb.buttons) == 2:
            kb.add_row()
        label = ""
        if group.id in selected:
            label = "✅ "

        kb.add_text_button(
            "{0}{1}".format(label, group.group_num),
            payload={"button": "group", "group": group.id},
        )

    if kb.buttons[-1]:
        kb.add_row()

    kb.add_text_button("Сохранить", payload={"button": "mention_save_selected_groups"})

    return kb.get_keyboard()
