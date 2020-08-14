from json import JSONDecoder
from typing import Dict

import hyperjson
from vkwave.bots import BaseEvent
from vkwave.bots import BotType
from vkwave.bots import PayloadFilter
from vkwave.bots.core import BaseFilter
from vkwave.bots.core.dispatching.filters.base import FilterResult
from vkwave.bots.core.dispatching.filters.builtin import is_message_event

from database import utils as db


class PLFilter(PayloadFilter):
    def __init__(
        self, payload: Dict[str, str], json_loader: JSONDecoder = hyperjson.loads,
    ):
        super().__init__(payload, json_loader)

    async def check(self, event: BaseEvent) -> FilterResult:
        is_message_event(event)
        if event.bot_type is BotType.USER:
            current_payload = event.object.object.message_data.payload
        else:
            if event.object.object.dict().get("message") is None:
                return FilterResult(False)
            current_payload = event.object.object.message.payload
        if current_payload is None:
            return FilterResult(False)
        return FilterResult(
            self.json_loader(current_payload).items() <= self.payload.items()
            or self.json_loader(current_payload).items() >= self.payload.items()
        )


class StateFilter(BaseFilter):
    def __init__(self, state):
        self.state = db.bot.get_id_of_state(state)

    async def check(self, event: BaseEvent) -> FilterResult:
        current_state = db.admin.get_admin_storage(
            db.students.get_system_id_of_student(event.object.object.message.peer_id)
        ).state_id.id
        return FilterResult(current_state == self.state)
