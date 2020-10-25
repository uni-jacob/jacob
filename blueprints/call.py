import os
import random

import hyperjson
from loguru import logger
from vkwave.api import API
from vkwave.bots import DefaultRouter
from vkwave.bots import MessageFromConversationTypeFilter
from vkwave.bots import SimpleBotEvent
from vkwave.bots import simple_bot_message_handler
from vkwave.client import AIOHTTPClient

from database import utils as db
from database.models import Chat
from database.models import Student
from services import call
from services import filters
from services import keyboard as kbs
from services import media
from services.exceptions import EmptyCallMessage
from services.logger.config import config

call_router = DefaultRouter()
api_session = API(tokens=os.getenv("VK_TOKEN"), clients=AIOHTTPClient())
api = api_session.get_context()
logger.configure(**config)


@simple_bot_message_handler(
    call_router,
    filters.PLFilter({"button": "call"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def start_call(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        if db.chats.get_list_of_chats_by_group(
            db.students.get_system_id_of_student(ans.object.object.message.from_id),
        ):
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


@simple_bot_message_handler(
    call_router,
    filters.PLFilter({"button": "cancel_call"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def cancel_call(ans: SimpleBotEvent):
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


@simple_bot_message_handler(
    call_router,
    filters.PLFilter({"button": "skip_call_message"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def skip_register_call_message(ans: SimpleBotEvent):
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


@simple_bot_message_handler(
    call_router,
    filters.StateFilter("wait_call_text"),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def register_call_message(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        attachments = ""
        if raw_attachments := ans.object.object.message.attachments:
            attachments = await media.load_attachments(
                api,
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


@simple_bot_message_handler(
    call_router,
    filters.PLFilter({"button": "half"}),
    filters.StateFilter("select_mentioned"),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def select_half(ans: SimpleBotEvent):
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


@simple_bot_message_handler(
    call_router,
    filters.PLFilter({"button": "letter"}),
    filters.StateFilter("select_mentioned"),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def select_letter(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = hyperjson.loads(ans.object.object.message.payload)
        letter = payload["value"]
        await ans.answer(
            f"Список студентов на букву {letter}",
            keyboard=kbs.call.CallNavigator(
                db.students.get_system_id_of_student(
                    ans.object.object.message.peer_id,
                ),
            )
            .render()
            .students(letter),
        )


@simple_bot_message_handler(
    call_router,
    filters.PLFilter({"button": "student"}),
    filters.StateFilter("select_mentioned"),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def select_student(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = hyperjson.loads(ans.object.object.message.payload)
        student_id = payload["student_id"]
        letter = payload["letter"]
        name = payload["name"]
        if student_id in db.shortcuts.get_list_of_calling_students(
            db.students.get_system_id_of_student(ans.object.object.message.peer_id),
        ):
            db.shortcuts.pop_student_from_calling_list(
                db.students.get_system_id_of_student(ans.object.object.message.peer_id),
                student_id,
            )
            label = "удален из списка призыва"
        else:
            db.shortcuts.add_student_to_calling_list(
                db.students.get_system_id_of_student(ans.object.object.message.peer_id),
                student_id,
            )
            label = "добавлен в список призыва"
        await ans.answer(
            f"{name} {label}",
            keyboard=kbs.call.CallNavigator(
                db.students.get_system_id_of_student(ans.object.object.message.peer_id),
            )
            .render()
            .students(letter),
        )


@simple_bot_message_handler(
    call_router,
    filters.PLFilter({"button": "save_selected"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def confirm_call(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        admin_id = db.students.get_system_id_of_student(
            ans.object.object.message.peer_id,
        )
        msg = call.generate_message(admin_id)
        store = db.admin.get_admin_storage(admin_id)
        chat_id = Chat.get_by_id(store.current_chat_id).chat_id
        try:
            query = await api.messages.get_conversations_by_id(chat_id)
            chat_name = query.response.items[0].chat_settings.title
        except IndexError:
            chat_name = "???"
        if not msg and not store.attaches:
            raise EmptyCallMessage("Сообщение призыва не может быть пустым")
        db.shortcuts.update_admin_storage(
            db.students.get_system_id_of_student(ans.object.object.message.peer_id),
            state_id=db.bot.get_id_of_state("confirm_call"),
        )
        await ans.answer(
            f'Сообщение будет отправлено в чат "{chat_name}":\n{msg}',
            keyboard=kbs.call.CallNavigator(
                db.students.get_system_id_of_student(ans.object.object.message.peer_id),
            )
            .render()
            .menu(),
            attachment=store.attaches or "",
        )


@simple_bot_message_handler(
    call_router,
    filters.PLFilter({"button": "call_all"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def call_them_all(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        admin_id = db.students.get_system_id_of_student(
            ans.object.object.message.peer_id,
        )
        student = Student.get_by_id(admin_id)
        students = [st.id for st in db.students.get_active_students(student.group_id)]
        db.shortcuts.update_calling_list(admin_id, students)
        await confirm_call(ans)


@simple_bot_message_handler(
    call_router,
    filters.StateFilter("confirm_call"),
    filters.PLFilter({"button": "confirm"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def send_call(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        admin_id = db.students.get_system_id_of_student(
            ans.object.object.message.peer_id,
        )
        store = db.admin.get_admin_storage(admin_id)
        msg = call.generate_message(admin_id)
        await api.messages.send(
            peer_id=Chat.get_by_id(store.current_chat_id).chat_id,
            message=msg,
            random_id=random.getrandbits(64),
            attachment=store.attaches or "",
        )
        db.shortcuts.clear_admin_storage(admin_id)
        await ans.answer(
            "Сообщение отправлено",
            keyboard=kbs.main.main_menu(admin_id),
        )


@simple_bot_message_handler(
    call_router,
    filters.StateFilter("confirm_call"),
    filters.PLFilter({"button": "deny"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def deny_call(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        await cancel_call(ans)


@simple_bot_message_handler(
    call_router,
    filters.StateFilter("confirm_call"),
    filters.PLFilter({"button": "names_usage"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def change_names_usage(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        db.shortcuts.invert_names_usage(
            db.students.get_system_id_of_student(ans.object.object.message.peer_id),
        )
        await confirm_call(ans)


@simple_bot_message_handler(
    call_router,
    filters.StateFilter("confirm_call"),
    filters.PLFilter({"button": "chat_config"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def change_chat(ans: SimpleBotEvent):
    kb = await kbs.common.list_of_chats(
        db.students.get_system_id_of_student(ans.object.object.message.from_id),
    )
    await ans.answer("Выберите чат", keyboard=kb.get_keyboard())


@simple_bot_message_handler(
    call_router,
    filters.StateFilter("confirm_call"),
    filters.PLFilter({"button": "chat"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def select_chat(ans: SimpleBotEvent):
    payload = hyperjson.loads(ans.object.object.message.payload)
    db.shortcuts.update_admin_storage(
        db.students.get_system_id_of_student(ans.object.object.message.from_id),
        current_chat_id=payload["chat_id"],
    )
    await confirm_call(ans)
