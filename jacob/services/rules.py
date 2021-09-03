import json
from typing import Union

from vkbottle.dispatch.rules.bot import ABCMessageRule
from vkbottle.bot import Message
from vkbottle_types.events import MessageEvent

from jacob.database.utils.states import get_state_id_by_name
from jacob.database.utils.users import get_state_of_user


def get_payload(message: Union[MessageEvent, Message]) -> dict:
    try:
        payload = message.object.payload
    except AttributeError:
        payload = json.loads(message.payload or "{}")

    return payload


class EventPayloadContainsRule(ABCMessageRule):
    def __init__(self, payload_particular_part: dict):
        self.payload_particular_part = payload_particular_part

    async def check(self, message: Union[MessageEvent, Message]) -> bool:
        payload = get_payload(message)

        return all(payload.get(k) == v for k, v in self.payload_particular_part.items())


class StateRule(ABCMessageRule):
    def __init__(self, state_name: str):
        self.state_name = state_name

    async def check(self, message: Union[MessageEvent, Message]) -> bool:
        state_id = await get_state_of_user(message.from_id)
        user_state = await get_state_id_by_name(self.state_name)
        return state_id == user_state
