"""Блок Студенты."""
import re

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


@bots.simple_bot_message_handler(
    students_router,
    filters.PLFilter({"button": "get_contacts"})
    & filters.StateFilter("students_select_student"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _show_contacts(ans: bots.SimpleBotEvent):
    student_id = await redis.hget(
        "students_selected_students:{0}".format(ans.from_id),
        "student_id",
    )
    with orm.db_session:
        student = models.Student[student_id]
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
        keyboard=kbs.students.student_card(),
    )


@bots.simple_bot_message_handler(
    students_router,
    filters.PLFilter({"button": "edit_student"})
    & filters.StateFilter("students_select_student"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _edit_student_menu(ans: bots.SimpleBotEvent):
    await ans.answer("Меню редактирования студента", keyboard=kbs.students.edit_menu())


@bots.simple_bot_message_handler(
    students_router,
    filters.PLFilter({"button": "cancel"}),
    filters.StateFilter("students_edit_*"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _cancel_editing_student(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    state_store = managers.StateStorageManager(admin_id)
    state_store.update(state=state_store.get_id_of_state("students_select_student"))

    await ans.answer("Редактирование отменено", keyboard=kbs.students.edit_menu())


@bots.simple_bot_message_handler(
    students_router,
    filters.PLFilter({"button": "edit_name"})
    & filters.StateFilter("students_select_student"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _edit_student_name(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    state_store = managers.StateStorageManager(admin_id)
    state_store.update(state=state_store.get_id_of_state("students_edit_name"))

    await ans.answer("Введите новое имя", keyboard=kbs.common.cancel())


@bots.simple_bot_message_handler(
    students_router,
    filters.StateFilter("students_edit_name"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _save_new_student_name(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    state_store = managers.StateStorageManager(admin_id)
    state_store.update(state=state_store.get_id_of_state("students_select_student"))

    student_id = await redis.hget(
        "students_selected_students:{0}".format(ans.from_id),
        "student_id",
    )

    with orm.db_session:
        models.Student[student_id].set(first_name=ans.text)

    await ans.answer("Студент отредактирован", keyboard=kbs.students.edit_menu())


@bots.simple_bot_message_handler(
    students_router,
    filters.PLFilter({"button": "edit_surname"})
    & filters.StateFilter("students_select_student"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _edit_student_surname(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    state_store = managers.StateStorageManager(admin_id)
    state_store.update(state=state_store.get_id_of_state("students_edit_surname"))

    await ans.answer("Введите новую фамилию", keyboard=kbs.common.cancel())


@bots.simple_bot_message_handler(
    students_router,
    filters.StateFilter("students_edit_surname"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _save_new_student_surname(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    state_store = managers.StateStorageManager(admin_id)
    state_store.update(state=state_store.get_id_of_state("students_select_student"))

    student_id = await redis.hget(
        "students_selected_students:{0}".format(ans.from_id),
        "student_id",
    )

    with orm.db_session:
        models.Student[student_id].set(last_name=ans.text)

    await ans.answer("Студент отредактирован", keyboard=kbs.students.edit_menu())


@bots.simple_bot_message_handler(
    students_router,
    filters.PLFilter({"button": "edit_phone"})
    & filters.StateFilter("students_select_student"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _edit_student_phone(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    state_store = managers.StateStorageManager(admin_id)
    state_store.update(state=state_store.get_id_of_state("students_edit_phone"))

    await ans.answer("Введите номер телефона", keyboard=kbs.common.cancel())


@bots.simple_bot_message_handler(
    students_router,
    filters.StateFilter("students_edit_phone"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _save_new_student_phone(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    state_store = managers.StateStorageManager(admin_id)

    student_id = await redis.hget(
        "students_selected_students:{0}".format(ans.from_id),
        "student_id",
    )
    if re.match(r"^8[0-9]{3}[0-9]{3}[0-9]{4,6}$", ans.text):
        with orm.db_session:
            models.Student[student_id].set(phone_number=ans.text)
        state_store.update(state=state_store.get_id_of_state("students_select_student"))

        await ans.answer("Студент отредактирован", keyboard=kbs.students.edit_menu())
    else:
        await ans.answer("Неверный формат данных")


@bots.simple_bot_message_handler(
    students_router,
    filters.PLFilter({"button": "edit_email"})
    & filters.StateFilter("students_select_student"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _edit_student_email(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    state_store = managers.StateStorageManager(admin_id)
    state_store.update(state=state_store.get_id_of_state("students_edit_email"))

    await ans.answer("Введите электропочту", keyboard=kbs.common.cancel())


@bots.simple_bot_message_handler(
    students_router,
    filters.StateFilter("students_edit_email"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _save_new_student_email(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    state_store = managers.StateStorageManager(admin_id)

    student_id = await redis.hget(
        "students_selected_students:{0}".format(ans.from_id),
        "student_id",
    )
    if re.match(r"^[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+$", ans.text):
        with orm.db_session:
            models.Student[student_id].set(email=ans.text)
        state_store.update(state=state_store.get_id_of_state("students_select_student"))

        await ans.answer("Студент отредактирован", keyboard=kbs.students.edit_menu())
    else:
        await ans.answer("Неверный формат данных")
