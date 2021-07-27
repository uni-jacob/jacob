from vkbottle.dispatch.rules.bot import ABCMessageRule
from vkbottle_types.events import MessageEvent


class PayloadContainsRule(ABCMessageRule):
    def __init__(self, payload_particular_part: dict):
        self.payload_particular_part = payload_particular_part

    async def check(self, message: MessageEvent) -> bool:
        payload = message.object.payload
        return all(payload.get(k) == v for k, v in self.payload_particular_part.items())
