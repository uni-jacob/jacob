import logging

from sentry_sdk import set_user
from vkbottle import BaseMiddleware, MiddlewareResponse
from vkbottle.bot import Message


class ChangeSentryUser(BaseMiddleware):
    """Миддлварь для изменения юзера в событии Sentry."""

    async def pre(self, message: Message) -> MiddlewareResponse:
        """
        Устанавливает юзера Sentry в ИД ВК или отображаемое имя, если есть.

        Args:
              message: Объект сообщения для проверки

        Returns:
            MiddlewareResponse: Ответ от миддлвари (продолжение обработки события или нет)
        """
        user = await message.get_user()
        id_ = {"username": user.screen_name or str(message.peer_id)}
        set_user(id_)
        logging.info(f"Юзер Sentry установлен в {id_}")
        return MiddlewareResponse(True)

    async def post(
        self,
        message: Message,
        *args,
    ):
        """
        Очищает юзера Sentry.

        Args:
              message: Объект сообщения для проверки
              *args: Дополнительные параметры (не используются)
        """
        set_user(None)
        logging.info("Юзер Sentry очищен")
