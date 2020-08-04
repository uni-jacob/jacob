import json

from vkbottle import Message
from vkbottle.rule import AbstractMessageRule

from database import utils
from database.models import State


class ButtonRule(AbstractMessageRule):
    def __init__(self, button: str):
        self.button = button

    async def check(self, message: Message) -> bool:
        if message.payload is not None:
            payload = json.loads(message.payload)
            if payload["button"] == self.button:
                return True


class StateRule(AbstractMessageRule):
    def __init__(self, state: str):
        self.state = state

    async def check(self, message: Message) -> bool:
        store = await utils.get_storage(message.from_id)
        state_id = await utils.get_id_of_state(self.state)
        if store is not None and store["state_id"] == state_id:
            return True
