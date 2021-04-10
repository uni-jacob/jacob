from typing import List

from vkwave.bots import Keyboard

from jacob.database import models, redis
from jacob.database.utils import admin, students
from jacob.database.utils.storages import managers
from jacob.services.keyboard.navigator import base

JSONStr = str


class MentionNavigator(base.Navigator):
    async def _get_alphabet(self) -> List[str]:
        groups: List[int] = await redis.lget("active_groups")
        if not groups:
            groups = [admin.get_active_group(self.owner).id]

        return students.get_unique_second_name_letters_in_a_group(groups)

    async def _get_students_by_letter(
        self,
        letter: str,
    ) -> List[models.Student]:
        groups: List[int] = await redis.lget("active_groups:{0}".format(self.owner))
        if not groups:
            groups = [admin.get_active_group(self.owner).id]

        return students.get_list_of_students_by_letter(groups, letter)

    def menu(self) -> JSONStr:
        kb = self._halves_of_alphabet()

        if len(kb.buttons[-1]):
            kb.add_row()
        kb.add_text_button(text="✅ Сохранить", payload={"button": "save_selected"})
        kb.add_text_button(text="📜 Пресеты", payload={"button": "presets"})
        kb.add_row()
        kb.add_text_button(text="✏️ Изменить текст", payload={"button": "call"})
        kb.add_row()
        kb.add_text_button(text="🚫 Отмена", payload={"button": "cancel_call"})

        return kb.get_keyboard()

    def submenu(self, half: int) -> JSONStr:
        kb = self._half_of_alphabet(half)

        kb.add_text_button("◀️ Назад", payload={"button": "skip_call_message"})

        return kb.get_keyboard()

    async def students(self, letter: str) -> JSONStr:
        data = await self._get_students_by_letter(letter)

        selected = managers.MentionStorageManager(
            self.owner,
        ).get_mentioned_students()
        half_index = self._find_half_index_of_letter(letter)

        kb = Keyboard()

        for item in data:
            if len(kb.buttons[-1]) == 2:
                kb.add_row()
            label = ""
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
