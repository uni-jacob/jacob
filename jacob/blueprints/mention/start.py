"""Запуск и первоначальная настройка Призыва."""

import os

from loguru import logger
from pony import orm
from vkwave import api, bots, client

from jacob.database.utils import students, admin, chats
from jacob.database.utils.storages import managers
from jacob.services import filters
from jacob.services import keyboard as kbs
from jacob.services import media
from jacob.services.logger.config import config

call_start_router = bots.DefaultRouter()
api_session = api.API(
    tokens=os.getenv("VK_TOKEN"),
    clients=client.AIOHTTPClient(),
)
api_context = api_session.get_context()
logger.configure(**config)


@bots.simple_bot_message_handler(
    call_start_router,
    filters.PLFilter({"button": "call"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _start_call(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.object.object.message.from_id)
    group_id = admin.get_active_group(admin_id)
    with orm.db_session:
        if chats.get_list_of_chats_by_group(group_id):
            state_store = managers.StateStorageManager(admin_id)
            state_store.update(
                state=state_store.get_id_of_state("mention_wait_text"),
            )
            await ans.answer(
                "Отправьте сообщение к призыву. Можно добавить до 10 фотографий",
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
async def _cancel_call(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.object.object.message.from_id)
    managers.MentionStorageManager(admin_id).clear()
    await ans.answer(
        "Призыв отменён. Возврат на главную.",
        keyboard=kbs.main.main_menu(admin_id),
    )


@bots.simple_bot_message_handler(
    call_start_router,
    filters.StateFilter("mention_confirm"),
    filters.PLFilter({"button": "deny"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _deny_call(ans: bots.SimpleBotEvent):
    await _cancel_call(ans)


@bots.simple_bot_message_handler(
    call_start_router,
    filters.PLFilter({"button": "skip_call_message"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _skip_register_call_message(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.object.object.message.from_id)
    state_store = managers.StateStorageManager(admin_id)
    state_store.update(
        state=state_store.get_id_of_state("mention_select_student"),
    )
    await ans.answer(
        "Выберите призываемых студентов",
        keyboard=kbs.call.CallNavigator(admin_id).render().menu(),
    )


@bots.simple_bot_message_handler(
    call_start_router,
    filters.StateFilter("mention_wait_text"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _register_call_message(ans: bots.SimpleBotEvent):
    attachments = ""
    message = ans.object.object.message
    raw_attachments = message.attachments
    admin_id = students.get_system_id_of_student(message.from_id)
    if message.is_cropped:
        extended_message = await ans.api_ctx.messages.get_by_id(message.id)
        raw_attachments = extended_message.response.items[0].attachments
    if raw_attachments:
        attachments = await media.load_attachments(
            api_context,
            raw_attachments,
            ans.object.object.message.peer_id,
        )
        await ans.answer("Загрузка вложений может занять некоторое время")
    state_store = managers.StateStorageManager(admin_id)
    state_store.update(
        state=state_store.get_id_of_state("mention_select_mentioned"),
    )
    mention_store = managers.MentionStorageManager(admin_id)
    mention_store.update_text(ans.object.object.message.text)
    mention_store.update_attaches(attachments)
    await ans.answer(
        "Сообщение сохранено. Выберите призываемых студентов",
        keyboard=kbs.call.CallNavigator(admin_id).render().menu(),
    )
