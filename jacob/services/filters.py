from json import JSONDecoder
from typing import Dict

import hyperjson
from vkwave.bots import BaseEvent
from vkwave.bots import BotType
from vkwave.bots import PayloadFilter
from vkwave.bots.core import BaseFilter
from vkwave.bots.core.dispatching.filters.base import FilterResult
from vkwave.bots.core.dispatching.filters.base import NotFilter
from vkwave.bots.core.dispatching.filters.builtin import has_payload
from vkwave.types.bot_events import BotEventType

from database import utils as db
from services.exceptions import StudentNotFound


class PLFilter(PayloadFilter):
    def __init__(
        self,
        payload: Dict[str, str],
        json_loader: JSONDecoder = hyperjson.loads,
    ):
        super().__init__(payload, json_loader)

    async def check(self, event: BaseEvent) -> FilterResult:
        if not has_payload(event):
            return FilterResult(False)
        if event.bot_type is BotType.USER:
            current_payload = self.json_loader(event.object.object.message_data.payload)
        elif event.object.type == BotEventType.MESSAGE_EVENT.value:
            current_payload = event.object.object.payload
        else:
            current_payload = self.json_loader(event.object.object.message.payload)
        if current_payload is None:
            return FilterResult(False)
        return FilterResult(
            any(
                self.payload.get(key, None) == val
                for key, val in current_payload.items()
            ),
        )


class StateFilter(BaseFilter):
    def __init__(self, state):
        self.state = db.bot.get_id_of_state(state)

    def __invert__(self):
        return NotFilter(self)

    async def check(self, event: BaseEvent) -> FilterResult:
        try:
            admin_id = db.students.get_system_id_of_student(
                event.object.object.message.from_id,
            )
        except StudentNotFound:
            return FilterResult(False)
        if not db.admin.is_user_admin(admin_id):
            return FilterResult(False)
        current_state = db.admin.get_admin_storage(admin_id).state_id.id
        return FilterResult(current_state == self.state)
