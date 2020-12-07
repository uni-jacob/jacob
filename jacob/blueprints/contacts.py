import os

import hyperjson
from loguru import logger
from vkvawe import bots

from database import utils as db
from database import models
from services import filters
from services import keyboard as kbs
from services.logger import config as logger_config

contacts_router = bots.DefaultRouter()
logger.configure(**logger_config)


@bots.simple_bot_message_handler(
    contacts_router,
    filters.PLFilter({"button": "contacts"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _start_contacts(ans: bots.SimpleBotEvent):
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


@bots.simple_bot_message_handler(
    contacts_router,
    filters.PLFilter({"button": "half"}) & filters.StateFilter("select_student"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _select_half(ans: bots.SimpleBotEvent):
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


@bots.simple_bot_message_handler(
    contacts_router,
    filters.PLFilter({"button": "letter"}) & filters.StateFilter("select_student"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _select_letter(ans: bots.SimpleBotEvent):
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


@bots.simple_bot_message_handler(
    contacts_router,
    filters.PLFilter({"button": "student"}) & filters.StateFilter("select_student"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _select_student(ans: bots.SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = hyperjson.loads(ans.object.object.message.payload)
        db.shortcuts.update_admin_storage(
            db.students.get_system_id_of_student(
                ans.object.object.message.from_id,
            ),
            state_id=db.bot.get_id_of_state("main"),
        )
        student = models.Student.get_by_id(payload.get("student_id"))
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
