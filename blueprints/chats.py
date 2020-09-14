import os

from loguru import logger
from vkwave.api import API
from vkwave.bots import ChatActionFilter
from vkwave.bots import CommandsFilter
from vkwave.bots import DefaultRouter
from vkwave.bots import MessageFromConversationTypeFilter
from vkwave.bots import SimpleBotEvent
from vkwave.bots import simple_bot_message_handler
from vkwave.client import AIOHTTPClient

from database import utils as db
from services.logger.config import config
from services.media import translate_string

chats_router = DefaultRouter()
api_session = API(tokens=os.getenv("VK_TOKEN"), clients=AIOHTTPClient())
api = api_session.get_context()
logger.configure(**config)


@simple_bot_message_handler(
    chats_router,
    ChatActionFilter("chat_invite_user"),
    MessageFromConversationTypeFilter("from_chat"),
)
@logger.catch()
async def greeting(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        db.chats.get_or_create_cached_chat(ans.object.object.message.peer_id)
        await ans.answer("Привет!")


@simple_bot_message_handler(
    chats_router,
    CommandsFilter("tr"),
    MessageFromConversationTypeFilter("from_chat"),
)
@logger.catch()
async def tr_command(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        if msg := ans.object.object.message.reply_message:
            await ans.answer(
                translate_string(msg.text),
            )
        for msg in ans.object.object.message.fwd_messages:
            await ans.answer(translate_string(msg.text))
        if (
            not ans.object.object.message.reply_message
            and not ans.object.object.message.fwd_messages
        ):
            await ans.answer("Команда используется в ответ на сообщение")
