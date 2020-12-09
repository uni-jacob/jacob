"""Функционал в чатах."""

from loguru import logger
from vkwave import bots

from services import decorators
from services.logger import config as logger_config
from services.media import translate_string

chats_router = bots.DefaultRouter()
logger.configure(**logger_config.config)


@bots.simple_bot_message_handler(
    chats_router,
    bots.ChatActionFilter("chat_invite_user"),
)
@logger.catch()
@decorators.context_logger
async def _greeting(ans: bots.SimpleBotEvent):
    await ans.answer("Привет!")


@bots.simple_bot_message_handler(
    chats_router,
    bots.CommandsFilter("tr"),
    bots.MessageFromConversationTypeFilter("from_chat"),
)
@logger.catch()
@decorators.context_logger
async def _tr_command(ans: bots.SimpleBotEvent):
    message = ans.object.object.message
    rep_msg = message.reply_message
    if rep_msg is not None:
        await ans.answer(
            translate_string(rep_msg.text),
        )
    for fwd_msg in message.fwd_messages:
        await ans.answer(translate_string(fwd_msg.text))
    if not message.reply_message and not message.fwd_messages:
        await ans.answer("Команда используется в ответ на сообщение")
