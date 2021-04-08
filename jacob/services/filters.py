import re
from typing import Any, AnyStr, Callable, Dict, Optional

import ujson
from pony import orm
from vkwave.bots import BaseEvent, PayloadFilter, SimpleBotEvent
from vkwave.bots.core import BaseFilter
from vkwave.bots.core.dispatching import filters

from jacob.database import redis
from jacob.database.utils import admin, students
from jacob.database.utils.storages import managers
from jacob.services.exceptions import StudentNotFound


class PLFilter(PayloadFilter):
    def __init__(
        self,
        payload: Dict[str, str],
        json_loader: Callable[[AnyStr, bool], Any] = ujson.loads,
    ):
        super().__init__(payload, json_loader)

    async def check(self, event: BaseEvent) -> filters.base.FilterResult:
        payload: Optional[str] = filters.builtin.get_payload(event)

        if payload is None:
            return filters.base.FilterResult(False)

        current_payload = self.json_loader(payload)

        return filters.base.FilterResult(
            any(
                self.payload.get(key, None) == val
                for key, val in current_payload.items()
            ),
        )


class RedisStateFilter(BaseFilter):
    def __init__(self, state: str):
        self.state: str = state

    def __invert__(self) -> filters.base.NotFilter:
        return filters.base.NotFilter(self)

    async def check(self, event: SimpleBotEvent) -> filters.base.FilterResult:
        current_state: Optional[str] = await redis.hget(
            str(event.object.object.message.from_id),
            "state",
        )
        if current_state is None:
            return filters.base.FilterResult(False)
        return filters.base.FilterResult(bool(re.match(self.state, current_state)))


class StateFilter(BaseFilter):
    def __init__(self, state: str):
        self.state = state

    def __invert__(self) -> filters.base.NotFilter:
        return filters.base.NotFilter(self)

    async def check(self, event: BaseEvent) -> filters.base.FilterResult:
        try:
            with orm.db_session:
                admin_id: int = students.get_system_id_of_student(
                    event.object.object.message.from_id,
                )
        except StudentNotFound:
            return filters.base.FilterResult(False)
        if not admin.is_user_admin(admin_id):
            return filters.base.FilterResult(False)

        with orm.db_session:
            current_state: str = (
                managers.StateStorageManager(admin_id).get_or_create().state.description
            )
        return filters.base.FilterResult(bool(re.match(self.state, current_state)))
