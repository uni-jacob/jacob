import re
from json import JSONDecoder
from typing import Dict

import ujson
from pony import orm
from vkwave.bots import BaseEvent, BotType, PayloadFilter, SimpleBotEvent
from vkwave.bots.core import BaseFilter
from vkwave.bots.core.dispatching import filters
from vkwave.types.bot_events import BotEventType

from jacob.database import redis
from jacob.database.utils import admin, students
from jacob.database.utils.storages import managers
from jacob.services.exceptions import StudentNotFound


class PLFilter(PayloadFilter):
    def __init__(
        self,
        payload: Dict[str, str],
        json_loader: JSONDecoder = ujson.loads,
    ):
        super().__init__(payload, json_loader)

    async def check(self, event: BaseEvent) -> filters.base.FilterResult:
        if filters.builtin.get_payload(event) is None:
            return filters.base.FilterResult(False)
        if event.bot_type is BotType.USER:
            current_payload = self.json_loader(event.object.object.message_data.payload)
        elif event.object.type == BotEventType.MESSAGE_EVENT.value:
            current_payload = event.object.object.payload
        else:
            current_payload = self.json_loader(event.object.object.message.payload)
        if current_payload is None:
            return filters.base.FilterResult(False)
        return filters.base.FilterResult(
            any(
                self.payload.get(key, None) == val
                for key, val in current_payload.items()
            ),
        )


class RedisStateFilter(BaseFilter):
    def __init__(self, state: str):
        self.state = state

    def __invert__(self):
        return filters.base.NotFilter(self)

    async def check(self, event: SimpleBotEvent) -> filters.base.FilterResult:
        current_state = await redis.hget(
            str(event.object.object.message.from_id), "state"
        )
        if current_state is None:
            return filters.base.FilterResult(False)
        return filters.base.FilterResult(bool(re.match(self.state, current_state)))


class StateFilter(BaseFilter):
    def __init__(self, state):
        self.state = state

    def __invert__(self):
        return filters.base.NotFilter(self)

    async def check(self, event: BaseEvent) -> filters.base.FilterResult:
        try:
            with orm.db_session:
                admin_id = students.get_system_id_of_student(
                    event.object.object.message.from_id,
                )
        except StudentNotFound:
            return filters.base.FilterResult(False)
        if not admin.is_user_admin(admin_id):
            return filters.base.FilterResult(False)

        with orm.db_session:
            current_state = (
                managers.StateStorageManager(admin_id).get_or_create().state.description
            )
        return filters.base.FilterResult(bool(re.match(self.state, current_state)))
