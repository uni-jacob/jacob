from json import JSONDecoder
from typing import Dict

import hyperjson
from vkwave.bots import BaseEvent
from vkwave.bots import BotType
from vkwave.bots import PayloadFilter
from vkwave.bots.core import BaseFilter
from vkwave.bots.core.dispatching.filters.base import FilterResult
from vkwave.types.bot_events import BotEventType

from database import utils as db
from services.exceptions import StudentNotFound


class PLFilter(PayloadFilter):
    def __init__(
        self, payload: Dict[str, str], json_loader: JSONDecoder = hyperjson.loads,
    ):
        super().__init__(payload, json_loader)

    async def check(self, event: BaseEvent) -> FilterResult:
        if event.bot_type is BotType.USER:
            current_payload = event.object.object.message_data.payload
        else:
            if event.object.object.dict().get("message") is None:
                if event.object.type == BotEventType.MESSAGE_EVENT:
                    current_payload = event.object.object.payload
                else:
                    return FilterResult(False)
            else:
                current_payload = event.object.object.message.payload
        if current_payload is None:
            return FilterResult(False)
        if not isinstance(current_payload, dict):
            current_payload = self.json_loader(current_payload)
        return FilterResult(
            any(
                self.payload.get(key, None) == val
                for key, val in current_payload.items()
            )
        )


class StateFilter(BaseFilter):
    def __init__(self, state):
        self.state = db.bot.get_id_of_state(state)

    async def check(self, event: BaseEvent) -> FilterResult:
        try:
            admin_id = db.students.get_system_id_of_student(
                event.object.object.message.from_id
            )
        except StudentNotFound:
            return FilterResult(False)
        current_state = db.admin.get_admin_storage(admin_id).state_id.id
        return FilterResult(current_state == self.state)
