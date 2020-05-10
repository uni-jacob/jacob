from vkbottle.rule import AbstractMessageRule
from vkbottle import Message
import json


class ButtonRule(AbstractMessageRule):
    def __init__(self, button: str):
        self.button = button

    async def check(self, message: Message) -> bool:
        payload = json.loads(message.payload)
        if payload["button"] == self.button:
            return True
