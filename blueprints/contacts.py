import os

import hyperjson
from loguru import logger
from vkwave.api import API
from vkwave.bots import DefaultRouter
from vkwave.bots import MessageFromConversationTypeFilter
from vkwave.bots import SimpleBotEvent
from vkwave.bots import simple_bot_message_handler
from vkwave.client import AIOHTTPClient

from database import utils as db
from database.models import Student
from services import filters
from services import keyboard as kbs
from services.logger.config import config

contacts_router = DefaultRouter()
api_session = API(tokens=os.getenv("VK_TOKEN"), clients=AIOHTTPClient())
api = api_session.get_context()
logger.configure(**config)


@simple_bot_message_handler(
    contacts_router,
    filters.PLFilter({"button": "contacts"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def start_contacts(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        db.shortcuts.update_admin_storage(
            db.students.get_system_id_of_student(ans.object.object.message.from_id),
            state_id=db.bot.get_id_of_state("select_student"),
        )
        await ans.answer(
            "Выберите студента для отображения его контактной информации",
            keyboard=kbs.contacts.ContactsNavigator(
                db.students.get_system_id_of_student(
                    ans.object.object.message.from_id,
                ),
            )
            .render()
            .menu(),
        )


@simple_bot_message_handler(
    contacts_router,
    filters.PLFilter({"button": "half"}) & filters.StateFilter("select_student"),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def select_half(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = hyperjson.loads(ans.object.object.message.payload)
        await ans.answer(
            "Выберите студента",
            keyboard=kbs.contacts.ContactsNavigator(
                db.students.get_system_id_of_student(
                    ans.object.object.message.from_id,
                ),
            )
            .render()
            .submenu(
                payload.get("half"),
            ),
        )


@simple_bot_message_handler(
    contacts_router,
    filters.PLFilter({"button": "letter"}) & filters.StateFilter("select_student"),
    MessageFromConversationTypeFilter("from_pm"),
)
async def select_letter(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = hyperjson.loads(ans.object.object.message.payload)
        letter = payload.get("value")
        await ans.answer(
            f"Список студентов на букву {letter}",
            keyboard=kbs.contacts.ContactsNavigator(
                db.students.get_system_id_of_student(ans.object.object.message.peer_id),
            )
            .render()
            .students(letter),
        )


@simple_bot_message_handler(
    contacts_router,
    filters.PLFilter({"button": "student"}) & filters.StateFilter("select_student"),
    MessageFromConversationTypeFilter("from_pm"),
)
async def select_student(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = hyperjson.loads(ans.object.object.message.payload)
        db.shortcuts.update_admin_storage(
            db.students.get_system_id_of_student(
                ans.object.object.message.from_id,
            ),
            state_id=db.bot.get_id_of_state("main"),
        )
        student = Student.get_by_id(payload.get("student_id"))
        contacts = f"""
        Контакты {student.first_name} {student.second_name}:
        ВК: @id{student.vk_id}
        Email: {student.email or "Не указан"}
        Телефон: {student.phone_number or "Не указан"}
        """
        await ans.answer(
            contacts,
            keyboard=kbs.main.main_menu(
                db.students.get_system_id_of_student(ans.object.object.message.from_id),
            ),
        )
