"""Функционал в чатах."""

from loguru import logger
from vkwave import bots

from services.logger.config import config
from services.media import translate_string

chats_router = bots.DefaultRouter()
logger.configure(**config)


@bots.simple_bot_message_handler(
    chats_router,
    bots.ChatActionFilter("chat_invite_user"),
)
@logger.catch()
async def _greeting(ans: bots.SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        await ans.answer("Привет!")


@bots.simple_bot_message_handler(
    chats_router,
    bots.CommandsFilter("tr"),
    bots.MessageFromConversationTypeFilter("from_chat"),
)
@logger.catch()
async def _tr_command(ans: bots.SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
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
