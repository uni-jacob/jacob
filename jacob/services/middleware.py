import logging
from typing import List, Any

from sentry_sdk import set_user
from vkbottle import BaseMiddleware, ABCView, ABCHandler, MiddlewareResponse
from vkbottle.bot import Message


class ChangeSentryUser(BaseMiddleware):
    async def pre(self, message: Message):
        user = await message.get_user()
        set_user({"username": user.screen_name or str(message.peer_id)})
        return MiddlewareResponse(True)

    async def post(
        self,
        message: Message,
        view: "ABCView",
        handle_responses: List[Any],
        handlers: List["ABCHandler"],
    ):
        set_user(None)

        if not handlers:
            return

        logging.debug(f"{handlers} caught the event {message}")
