import os
import random

import hyperjson
from loguru import logger
from vkwave.api import API
from vkwave.bots import DefaultRouter
from vkwave.bots import SimpleBotEvent
from vkwave.bots import simple_bot_message_handler
from vkwave.client import AIOHTTPClient

from database import utils as db
from services import call
from services import filters
from services import keyboard as kbs
from services import media
from services.exceptions import EmptyCallMessage

call_router = DefaultRouter()
api_session = API(tokens=os.getenv("VK_TOKEN"), clients=AIOHTTPClient())
api = api_session.get_context()


@simple_bot_message_handler(call_router, filters.PLFilter({"button": "call"}))
@logger.catch()
async def start_call(ans: SimpleBotEvent):
    db.admin.update_admin_storage(
        db.students.get_system_id_of_student(ans.object.object.message.peer_id),
        state_id=db.bot.get_id_of_state("wait_call_text"),
    )
    await ans.answer(
        "Отправьте сообщение к призыву. Поддерживаются фотографии и документы",
        keyboard=kbs.call.skip_call_message(),
    )


@simple_bot_message_handler(call_router, filters.PLFilter({"button": "cancel_call"}))
@logger.catch()
async def cancel_call(ans: SimpleBotEvent):
    db.admin.clear_admin_storage(
        db.students.get_system_id_of_student(ans.object.object.message.peer_id)
    )
    await ans.answer(
        "Призыв отменён. Возврат на главную.",
        keyboard=kbs.main.main_menu(ans.object.object.message.peer_id),
    )


@simple_bot_message_handler(
    call_router, filters.PLFilter({"button": "skip_call_message"})
)
@logger.catch()
async def skip_register_call_message(ans: SimpleBotEvent):
    db.admin.update_admin_storage(
        db.students.get_system_id_of_student(ans.object.object.message.peer_id),
        state_id=db.bot.get_id_of_state("main"),
    )
    await ans.answer(
        "Выберите призываемых студентов",
        keyboard=kbs.call.call_interface(ans.object.object.message.peer_id),
    )


@simple_bot_message_handler(call_router, filters.StateFilter("wait_call_text"))
@logger.catch()
async def register_call_message(ans: SimpleBotEvent):
    attachments = ""
    if raw_attachments := ans.object.object.message.attachments:
        attachments = await media.load_attachments(
            api, raw_attachments, ans.object.object.message.peer_id
        )
    db.admin.update_admin_storage(
        db.students.get_system_id_of_student(ans.object.object.message.peer_id),
        state_id=db.bot.get_id_of_state("main"),
        text=ans.object.object.message.text,
        attaches=attachments,
    )
    await ans.answer(
        "Сообщение сохранено. Выберите призываемых студентов",
        keyboard=kbs.call.call_interface(ans.object.object.message.peer_id),
    )


@simple_bot_message_handler(call_router, filters.PLFilter({"button": "letter"}))
@logger.catch()
async def select_letter(ans: SimpleBotEvent):
    payload = ans.object.object.message.payload
    letter = hyperjson.loads(payload)["value"]
    await ans.answer(
        f"Список студентов на букву {letter}",
        keyboard=kbs.call.list_of_students(letter, ans.object.object.message.peer_id),
    )


@simple_bot_message_handler(call_router, filters.PLFilter({"button": "student"}))
@logger.catch()
async def select_student(ans: SimpleBotEvent):
    payload = hyperjson.loads(ans.object.object.message.payload)
    student_id = payload["student_id"]
    letter = payload["letter"]
    name = payload["name"]
    if student_id in db.shortcuts.get_list_of_calling_students(
        db.students.get_system_id_of_student(ans.object.object.message.peer_id)
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
        keyboard=kbs.call.list_of_students(letter, ans.object.object.message.peer_id),
    )


@simple_bot_message_handler(call_router, filters.PLFilter({"button": "save_selected"}))
@logger.catch()
async def confirm_call(ans: SimpleBotEvent):
    admin_id = db.students.get_system_id_of_student(ans.object.object.message.peer_id)
    msg = call.generate_message(admin_id)
    store = db.admin.get_admin_storage(admin_id)
    chat_type = store.current_chat.description.lower()
    if not msg and not store.attaches:
        raise EmptyCallMessage("Сообщение призыва не может быть пустым")
    db.admin.update_admin_storage(
        db.students.get_system_id_of_student(ans.object.object.message.peer_id),
        state_id=db.bot.get_id_of_state("confirm_call"),
    )
    await ans.answer(
        f"Сообщение будет отправлено в {chat_type} чат:\n{msg}",
        keyboard=kbs.call.call_prompt(
            db.students.get_system_id_of_student(ans.object.object.message.peer_id)
        ),
        attachment=store.attaches or "",
    )


@simple_bot_message_handler(call_router, filters.PLFilter({"button": "call_all"}))
@logger.catch()
async def call_them_all(ans: SimpleBotEvent):
    admin_id = db.students.get_system_id_of_student(ans.object.object.message.peer_id)
    student = db.students.find_student(id=admin_id)
    students = [st.id for st in db.students.get_active_students(student.group_id)]
    db.shortcuts.update_calling_list(admin_id, students)
    await confirm_call(ans)


@simple_bot_message_handler(
    call_router,
    filters.StateFilter("confirm_call"),
    filters.PLFilter({"button": "confirm"}),
)
@logger.catch()
async def send_call(ans: SimpleBotEvent):
    admin_id = db.students.get_system_id_of_student(ans.object.object.message.peer_id)
    store = db.admin.get_admin_storage(admin_id)
    msg = call.generate_message(admin_id)
    await api.messages.send(
        peer_id=db.shortcuts.get_active_chat(admin_id).chat_id,
        message=msg,
        random_id=random.getrandbits(64),
        attachment=store.attaches or "",
    )
    db.admin.clear_admin_storage(admin_id)
    await ans.answer(
        "Сообщение отправлено",
        keyboard=kbs.main.main_menu(ans.object.object.message.peer_id),
    )


@simple_bot_message_handler(
    call_router,
    filters.StateFilter("confirm_call"),
    filters.PLFilter({"button": "deny"}),
)
@logger.catch()
async def deny_call(ans: SimpleBotEvent):
    await cancel_call(ans)


@simple_bot_message_handler(
    call_router,
    filters.StateFilter("confirm_call"),
    filters.PLFilter({"button": "names_usage"}),
)
@logger.catch()
async def change_names_usage(ans: SimpleBotEvent):
    db.shortcuts.invert_names_usage(
        db.students.get_system_id_of_student(ans.object.object.message.peer_id)
    )
    await confirm_call(ans)


@simple_bot_message_handler(
    call_router,
    filters.StateFilter("confirm_call"),
    filters.PLFilter({"button": "chat_config"}),
)
@logger.catch()
async def change_chat(ans: SimpleBotEvent):
    db.shortcuts.invert_current_chat(
        db.students.get_system_id_of_student(ans.object.object.message.peer_id)
    )
    await confirm_call(ans)
