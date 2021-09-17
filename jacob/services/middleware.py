import logging
from typing import Any, List

from sentry_sdk import set_user
from vkbottle import ABCHandler, ABCView, BaseMiddleware, MiddlewareResponse
from vkbottle.bot import Message


class ChangeSentryUser(BaseMiddleware):
    """Миддлварь для изменения юзера в событии Sentry."""

    async def pre(self, message: Message):
        """Устанавливает юзера Sentry в ИД ВК или отображаемое имя, если есть."""
        user = await message.get_user()
        id_ = {"username": user.screen_name or str(message.peer_id)}
        set_user(id_)
        logging.info(f"Юзер Sentry установлен в {id_}")
        return MiddlewareResponse(True)

    async def post(
        self,
        message: Message,
        view: "ABCView",
        handle_responses: List[Any],
        handlers: List["ABCHandler"],
    ):
        """Очищает юзера Sentry."""
        set_user(None)
        logging.info("Юзер Sentry очищен")
