"""Запуск и первоначальная настройка Призыва."""

import os

from loguru import logger
from vkwave import api, bots, client

from database import utils as db
from services import decorators, filters
from services import keyboard as kbs
from services import media
from services.logger.config import config

call_start_router = bots.DefaultRouter()
api_session = api.API(
    tokens=os.getenv("VK_CANARY_TOKEN"),
    clients=client.AIOHTTPClient(),
)
api_context = api_session.get_context()
logger.configure(**config)


@bots.simple_bot_message_handler(
    call_start_router,
    filters.PLFilter({"button": "call"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
@decorators.context_logger
async def _start_call(ans: bots.SimpleBotEvent):
    admin_id = db.students.get_system_id_of_student(ans.object.object.message.from_id)
    group_id = db.admin.get_active_group(admin_id)
    if db.chats.get_list_of_chats_by_group(group_id):
        db.shortcuts.update_admin_storage(
            admin_id,
            state_id=db.bot.get_id_of_state("wait_call_text"),
        )
        await ans.answer(
            "Отправьте сообщение к призыву. Поддерживаются фотографии и документы",
            keyboard=kbs.call.skip_call_message(),
        )
    else:
        await ans.answer(
            "У вашей группы нет зарегистрированных чатов. Возврат в главное меню",
        )


@bots.simple_bot_message_handler(
    call_start_router,
    filters.PLFilter({"button": "cancel_call"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
@decorators.context_logger
async def _cancel_call(ans: bots.SimpleBotEvent):
    admin_id = db.students.get_system_id_of_student(ans.object.object.message.from_id)
    db.shortcuts.clear_admin_storage(admin_id)
    await ans.answer(
        "Призыв отменён. Возврат на главную.",
        keyboard=kbs.main.main_menu(admin_id),
    )


@bots.simple_bot_message_handler(
    call_start_router,
    filters.StateFilter("confirm_call"),
    filters.PLFilter({"button": "deny"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
@decorators.context_logger
async def _deny_call(ans: bots.SimpleBotEvent):
    await _cancel_call(ans)


@bots.simple_bot_message_handler(
    call_start_router,
    filters.PLFilter({"button": "skip_call_message"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
@decorators.context_logger
async def _skip_register_call_message(ans: bots.SimpleBotEvent):
    admin_id = db.students.get_system_id_of_student(ans.object.object.message.from_id)
    db.shortcuts.update_admin_storage(
        admin_id,
        state_id=db.bot.get_id_of_state("select_mentioned"),
    )
    await ans.answer(
        "Выберите призываемых студентов",
        keyboard=kbs.call.CallNavigator(admin_id).render().menu(),
    )


@bots.simple_bot_message_handler(
    call_start_router,
    filters.StateFilter("wait_call_text"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
@decorators.context_logger
async def _register_call_message(ans: bots.SimpleBotEvent):
    attachments = ""
    raw_attachments = ans.object.object.message.attachments
    admin_id = db.students.get_system_id_of_student(ans.object.object.message.from_id)
    if raw_attachments is not None:
        attachments = await media.load_attachments(
            api_context,
            raw_attachments,
            ans.object.object.message.peer_id,
        )
    db.shortcuts.update_admin_storage(
        admin_id,
        state_id=db.bot.get_id_of_state("select_mentioned"),
        text=ans.object.object.message.text,
        attaches=attachments,
    )
    await ans.answer(
        "Сообщение сохранено. Выберите призываемых студентов",
        keyboard=kbs.call.CallNavigator(admin_id).render().menu(),
    )
