"""Блок Студенты."""

from loguru import logger
from pony import orm
from vkwave import bots

from jacob.database import models, redis
from jacob.database.utils import students
from jacob.database.utils.storages import managers
from jacob.services import filters
from jacob.services import keyboard as kbs
from jacob.services.logger import config as logger_config

students_router = bots.DefaultRouter()
logger.configure(**logger_config.config)


@bots.simple_bot_message_handler(
    students_router,
    filters.PLFilter({"button": "students"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _start_students(ans: bots.SimpleBotEvent):
    state_storage = managers.StateStorageManager(
        students.get_system_id_of_student(ans.from_id)
    )
    state_storage.update(state=state_storage.get_id_of_state("students_select_student"))
    await ans.answer(
        "Выберите студента",
        keyboard=kbs.contacts.ContactsNavigator(
            students.get_system_id_of_student(
                ans.from_id,
            ),
        )
        .render()
        .menu(),
    )


@bots.simple_bot_message_handler(
    students_router,
    filters.PLFilter({"button": "half"})
    & filters.StateFilter("students_select_student"),
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
    students_router,
    filters.PLFilter({"button": "letter"})
    & filters.StateFilter("students_select_student"),
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
    students_router,
    filters.PLFilter({"button": "student"})
    & filters.StateFilter("students_select_student"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _select_student(ans: bots.SimpleBotEvent):
    student_id = ans.payload.get("student_id")

    with orm.db_session:
        student = models.Student[student_id]

    await redis.hmset(
        "students_selected_students:{0}".format(ans.from_id),
        student_id=student_id,
    )

    await ans.answer(
        "Студент {0} {1}".format(student.first_name, student.last_name),
        keyboard=kbs.students.student_card(),
    )
