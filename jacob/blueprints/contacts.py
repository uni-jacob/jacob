"""Блок Контакты."""

from loguru import logger
from pony import orm
from vkwave import bots

from jacob.database import models
from jacob.database.utils import students
from jacob.database.utils.storages import managers
from jacob.services import filters
from jacob.services import keyboard as kbs
from jacob.services.logger import config as logger_config

contacts_router = bots.DefaultRouter()
logger.configure(**logger_config.config)


@bots.simple_bot_message_handler(
    contacts_router,
    filters.PLFilter({"button": "contacts"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _start_contacts(ans: bots.SimpleBotEvent):
    state_storage = managers.StateStorageManager(
        students.get_system_id_of_student(ans.from_id)
    )
    state_storage.update(state=state_storage.get_id_of_state("contacts_select_student"))
    await ans.answer(
        "Выберите студента для отображения его контактной информации",
        keyboard=kbs.contacts.ContactsNavigator(
            students.get_system_id_of_student(
                ans.from_id,
            ),
        )
        .render()
        .menu(),
    )


@bots.simple_bot_message_handler(
    contacts_router,
    filters.PLFilter({"button": "half"})
    & filters.StateFilter("contacts_select_student"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _select_half(ans: bots.SimpleBotEvent):
    await ans.answer(
        "Выберите студента",
        keyboard=kbs.contacts.ContactsNavigator(
            students.get_system_id_of_student(
                ans.object.object.message.from_id,
            ),
        )
        .render()
        .submenu(
            ans.payload.get("half"),
        ),
    )


@bots.simple_bot_message_handler(
    contacts_router,
    filters.PLFilter({"button": "letter"})
    & filters.StateFilter("contacts_select_student"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _select_letter(ans: bots.SimpleBotEvent):
    letter = ans.payload.get("value")
    await ans.answer(
        "Список студентов на букву {0}".format(letter),
        keyboard=kbs.contacts.ContactsNavigator(
            students.get_system_id_of_student(ans.from_id),
        )
        .render()
        .students(letter),
    )


@bots.simple_bot_message_handler(
    contacts_router,
    filters.PLFilter({"button": "student"})
    & filters.StateFilter("contacts_select_student"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _select_student(ans: bots.SimpleBotEvent):
    state_storage = managers.StateStorageManager(
        students.get_system_id_of_student(ans.from_id)
    )
    state_storage.update(state=state_storage.get_id_of_state("main"))
    with orm.db_session:
        student = models.Student[ans.payload.get("student_id")]
    email = student.email or "Не указан"
    phone_number = student.phone_number or "Не указан"
    contacts = "Контакты {0} {1}:\nВК: @id{2}\nEmail: {3}\nТелефон: {4}".format(
        student.first_name,
        student.last_name,
        student.vk_id,
        email,
        phone_number,
    )
    await ans.answer(
        contacts,
        keyboard=kbs.main.main_menu(
            students.get_system_id_of_student(ans.from_id),
        ),
    )
