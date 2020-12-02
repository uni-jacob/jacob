"""Блок Призыв."""

# TODO:
#   - WPS202 Found too many module members: 14 > 7
#   - WPS204 Found overused expression: logger.contextualize(...)
#   - WPS210 Found too many local variables: 7 > 5 _confirm_call(...)


import os
import random

import hyperjson
from loguru import logger
from vkwave import api, bots, client

from database import models
from database import utils as db
from services import call, filters
from services import keyboard as kbs
from services import media
from services.exceptions import EmptyCallMessage
from services.logger.config import config

call_router = bots.DefaultRouter()
api_session = api.API(tokens=os.getenv("VK_TOKEN"), clients=client.AIOHTTPClient())
api_context = api_session.get_context()
logger.configure(**config)


@bots.simple_bot_message_handler(
    call_router,
    filters.PLFilter({"button": "call"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _start_call(ans: bots.SimpleBotEvent):
    # TODO: Вытащить contextualize в декоратор
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        group_id = db.admin.get_active_group(
            db.students.get_system_id_of_student(ans.object.object.message.from_id),
        )
        if db.chats.get_list_of_chats_by_group(group_id):
            db.shortcuts.update_admin_storage(
                db.students.get_system_id_of_student(ans.object.object.message.peer_id),
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
    call_router,
    filters.PLFilter({"button": "cancel_call"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _cancel_call(ans: bots.SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        db.shortcuts.clear_admin_storage(
            db.students.get_system_id_of_student(ans.object.object.message.peer_id),
        )
        await ans.answer(
            "Призыв отменён. Возврат на главную.",
            keyboard=kbs.main.main_menu(
                db.students.get_system_id_of_student(ans.object.object.message.peer_id),
            ),
        )


@bots.simple_bot_message_handler(
    call_router,
    filters.PLFilter({"button": "skip_call_message"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _skip_register_call_message(ans: bots.SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        db.shortcuts.update_admin_storage(
            db.students.get_system_id_of_student(ans.object.object.message.peer_id),
            state_id=db.bot.get_id_of_state("select_mentioned"),
        )
        await ans.answer(
            "Выберите призываемых студентов",
            keyboard=kbs.call.CallNavigator(
                db.students.get_system_id_of_student(ans.object.object.message.peer_id),
            )
            .render()
            .menu(),
        )


@bots.simple_bot_message_handler(
    call_router,
    filters.StateFilter("wait_call_text"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _register_call_message(ans: bots.SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        attachments = ""
        raw_attachments = ans.object.object.message.attachments
        if raw_attachments is not None:
            attachments = await media.load_attachments(
                api_context,
                raw_attachments,
                ans.object.object.message.peer_id,
            )
        db.shortcuts.update_admin_storage(
            db.students.get_system_id_of_student(ans.object.object.message.peer_id),
            state_id=db.bot.get_id_of_state("select_mentioned"),
            text=ans.object.object.message.text,
            attaches=attachments,
        )
        await ans.answer(
            "Сообщение сохранено. Выберите призываемых студентов",
            keyboard=kbs.call.CallNavigator(
                db.students.get_system_id_of_student(ans.object.object.message.peer_id),
            )
            .render()
            .menu(),
        )


@bots.simple_bot_message_handler(
    call_router,
    filters.PLFilter({"button": "half"}),
    filters.StateFilter("select_mentioned"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _select_half(ans: bots.SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = hyperjson.loads(ans.object.object.message.payload)
        await ans.answer(
            "Выберите призываемых студентов",
            keyboard=kbs.call.CallNavigator(
                db.students.get_system_id_of_student(ans.object.object.message.peer_id),
            )
            .render()
            .submenu(payload["half"]),
        )


@bots.simple_bot_message_handler(
    call_router,
    filters.PLFilter({"button": "letter"}),
    filters.StateFilter("select_mentioned"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _select_letter(ans: bots.SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = hyperjson.loads(ans.object.object.message.payload)
        letter = payload["value"]
        await ans.answer(
            "Список студентов на букву {0}".format(letter),
            keyboard=kbs.call.CallNavigator(
                db.students.get_system_id_of_student(
                    ans.object.object.message.peer_id,
                ),
            )
            .render()
            .students(letter),
        )


@bots.simple_bot_message_handler(
    call_router,
    filters.PLFilter({"button": "student"}),
    filters.StateFilter("select_mentioned"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _select_student(ans: bots.SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = hyperjson.loads(ans.object.object.message.payload)
        student_id = payload["student_id"]
        admin_id = db.students.get_system_id_of_student(
            ans.object.object.message.peer_id,
        )
        if student_id in db.shortcuts.get_list_of_calling_students(admin_id):
            db.shortcuts.pop_student_from_calling_list(
                admin_id,
                student_id,
            )
            label = "удален из списка призыва"
        else:
            db.shortcuts.add_student_to_calling_list(
                admin_id,
                student_id,
            )
            label = "добавлен в список призыва"
        await ans.answer(
            "{0} {1}".format(payload["name"], label),
            keyboard=kbs.call.CallNavigator(
                admin_id,
            )
            .render()
            .students(payload["letter"]),
        )


@bots.simple_bot_message_handler(
    call_router,
    filters.PLFilter({"button": "save_selected"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _confirm_call(ans: bots.SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        admin_id = db.students.get_system_id_of_student(
            ans.object.object.message.peer_id,
        )
        msg = call.generate_message(admin_id)
        store = db.admin.get_admin_storage(admin_id)
        chat_id = models.Chat.get_by_id(store.current_chat_id).chat_id
        query = await api_context.messages.get_conversations_by_id(chat_id)
        try:
            chat_settings = query.response.items[0].chat_settings
        except IndexError:
            chat_name = "???"
        else:
            chat_name = chat_settings.title
        if not msg and not store.attaches:
            raise EmptyCallMessage("Сообщение призыва не может быть пустым")
        db.shortcuts.update_admin_storage(
            admin_id,
            state_id=db.bot.get_id_of_state("confirm_call"),
        )
        await ans.answer(
            'Сообщение будет отправлено в чат "{0}":\n{1}'.format(chat_name, msg),
            keyboard=kbs.call.call_prompt(
                admin_id,
            ),
            attachment=store.attaches or "",
        )


@bots.simple_bot_message_handler(
    call_router,
    filters.PLFilter({"button": "call_all"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _call_them_all(ans: bots.SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        admin_id = db.students.get_system_id_of_student(
            ans.object.object.message.peer_id,
        )
        student = models.Student.get_by_id(admin_id)
        students = [st.id for st in db.students.get_active_students(student.group_id)]
        db.shortcuts.update_calling_list(admin_id, students)
        await _confirm_call(ans)


@bots.simple_bot_message_handler(
    call_router,
    filters.StateFilter("confirm_call"),
    filters.PLFilter({"button": "confirm"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _send_call(ans: bots.SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        admin_id = db.students.get_system_id_of_student(
            ans.object.object.message.peer_id,
        )
        store = db.admin.get_admin_storage(admin_id)
        msg = call.generate_message(admin_id)
        bits = 64
        await api_context.messages.send(
            peer_id=models.Chat.get_by_id(store.current_chat_id).chat_id,
            message=msg,
            random_id=random.getrandbits(bits),
            attachment=store.attaches or "",
        )
        db.shortcuts.clear_admin_storage(admin_id)
        await ans.answer(
            "Сообщение отправлено",
            keyboard=kbs.main.main_menu(admin_id),
        )


@bots.simple_bot_message_handler(
    call_router,
    filters.StateFilter("confirm_call"),
    filters.PLFilter({"button": "deny"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _deny_call(ans: bots.SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        await _cancel_call(ans)


@bots.simple_bot_message_handler(
    call_router,
    filters.StateFilter("confirm_call"),
    filters.PLFilter({"button": "names_usage"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _change_names_usage(ans: bots.SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        db.shortcuts.invert_names_usage(
            db.students.get_system_id_of_student(ans.object.object.message.peer_id),
        )
        await _confirm_call(ans)


@bots.simple_bot_message_handler(
    call_router,
    filters.StateFilter("confirm_call"),
    filters.PLFilter({"button": "chat_config"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _change_chat(ans: bots.SimpleBotEvent):
    kb = await kbs.common.list_of_chats(
        db.students.get_system_id_of_student(ans.object.object.message.from_id),
    )
    await ans.answer("Выберите чат", keyboard=kb.get_keyboard())


@bots.simple_bot_message_handler(
    call_router,
    filters.StateFilter("confirm_call"),
    filters.PLFilter({"button": "chat"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _select_chat(ans: bots.SimpleBotEvent):
    payload = hyperjson.loads(ans.object.object.message.payload)
    db.shortcuts.update_admin_storage(
        db.students.get_system_id_of_student(ans.object.object.message.from_id),
        current_chat_id=payload["chat_id"],
    )
    await _confirm_call(ans)
