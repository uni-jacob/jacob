import logging

from sentry_sdk import set_user
from vkbottle import BaseMiddleware
from vkbottle.bot import Message


class ChangeSentryUser(BaseMiddleware[Message]):
    """Миддлварь для изменения юзера в событии Sentry."""

    async def pre(self):
        """
        Устанавливает юзера Sentry в ИД ВК или отображаемое имя, если есть.
        """
        user = await self.event.get_user()
        id_ = {"username": user.screen_name or str(self.event.peer_id)}
        set_user(id_)
        logging.info(f"Юзер Sentry установлен в {id_}")

    async def post(self):
        """
        Очищает юзера Sentry.
        """
        set_user(None)
        logging.info("Юзер Sentry очищен")
