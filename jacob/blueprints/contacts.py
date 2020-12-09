"""Блок Контакты."""

import ujson
from loguru import logger
from vkwave import bots

from database import models
from database import utils as db
from services import decorators, filters
from services import keyboard as kbs
from services.logger import config as logger_config

contacts_router = bots.DefaultRouter()
logger.configure(**logger_config.config)


@bots.simple_bot_message_handler(
    contacts_router,
    filters.PLFilter({"button": "contacts"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
@decorators.context_logger
async def _start_contacts(ans: bots.SimpleBotEvent):
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
@decorators.context_logger
async def _select_half(ans: bots.SimpleBotEvent):
    payload = ujson.loads(ans.object.object.message.payload)
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
@logger.catch()
@decorators.context_logger
async def _select_letter(ans: bots.SimpleBotEvent):
    payload = ujson.loads(ans.object.object.message.payload)
    letter = payload.get("value")
    await ans.answer(
        "Список студентов на букву {0}".format(letter),
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
@logger.catch
@decorators.context_logger
async def _select_student(ans: bots.SimpleBotEvent):
    payload = ujson.loads(ans.object.object.message.payload)
    db.shortcuts.update_admin_storage(
        db.students.get_system_id_of_student(
            ans.object.object.message.from_id,
        ),
        state_id=db.bot.get_id_of_state("main"),
    )
    student = models.Student.get_by_id(payload.get("student_id"))
    email = student.email or "Не указан"
    phone_number = student.phone_number or "Не указан"
    contacts = "Контакты {0} {1}:\nВК: @id{2}\nEmail: {3}Телефон: {4}".format(
        student.first_name,
        student.second_name,
        student.vk_id,
        email,
        phone_number,
    )
    await ans.answer(
        contacts,
        keyboard=kbs.main.main_menu(
            db.students.get_system_id_of_student(ans.object.object.message.from_id),
        ),
    )
