import json
import re

from vkbottle import EMPTY_KEYBOARD
from vkbottle.bot import Blueprint, Message

from jacob.database.utils.schedule.days import get_days
from jacob.database.utils.schedule.lesson import find_lesson
from jacob.database.utils.schedule.lesson_storage import (
    get_or_create_lesson_storage,
    update_lesson_storage,
)
from jacob.database.utils.schedule.lesson_types import get_lesson_types
from jacob.database.utils.schedule.timetable import (
    create_lesson_time,
    get_timetable,
)
from jacob.database.utils.students import get_student
from jacob.database.utils.universities import find_university_of_user
from jacob.database.utils.users import get_user_id, set_state
from jacob.services import keyboards
from jacob.services.common import vbml_rule
from jacob.services.middleware import ChangeSentryUser
from jacob.services.rules import EventPayloadContainsRule, StateRule

bp = Blueprint("Schedule:select_slot")
bp.labeler.message_view.register_middleware(ChangeSentryUser())
vbml_rule = vbml_rule(bp)


@bp.on.message(
    EventPayloadContainsRule({"block": "schedule"}),
    EventPayloadContainsRule(
        {"action": "select:week"},
    ),
)
async def select_week(message: Message):
    payload = json.loads(message.payload)
    user_id = await get_user_id(message.peer_id)
    await get_or_create_lesson_storage(user_id)
    await update_lesson_storage(
        user_id,
        week_id=payload.get("week"),
    )
    await set_state(message.peer_id, "schedule:edit:select_day")
    days = await get_days()
    await message.answer("Выберите день", keyboard=keyboards.days(days))


@bp.on.message(
    EventPayloadContainsRule({"block": "schedule"}),
    EventPayloadContainsRule(
        {"action": "select:day"},
    ),
)
async def select_day(message: Message):
    payload = json.loads(message.payload)
    user_id = await get_user_id(message.peer_id)
    await update_lesson_storage(
        user_id,
        day_id=payload.get("day"),
    )
    await set_state(message.peer_id, "schedule:edit:select_time")
    university = await find_university_of_user(await get_user_id(message.peer_id))
    timetable = await get_timetable(university.id)
    await message.answer(
        "Выберите время занятия",
        keyboard=keyboards.timetable(timetable),
    )


@bp.on.message(
    EventPayloadContainsRule({"block": "schedule"}),
    EventPayloadContainsRule(
        {"action": "create:time"},
    ),
)
async def create_time(message: Message):
    await set_state(message.peer_id, "schedule:create_time")
    await message.answer(
        'Введите время начала и время конца занятия в формате "ЧЧ:ММ-ЧЧ:ММ"',
        keyboard=EMPTY_KEYBOARD,
    )


@bp.on.message(
    vbml_rule("<time>"),
    StateRule("schedule:create_time"),
)
async def save_time(message: Message, time: str):
    if re.match(r"^\d{2}:\d{2}-\d{2}:\d{2}$", time):
        university = await find_university_of_user(await get_user_id(message.peer_id))
        start_time, end_time = time.split("-")
        await create_lesson_time(university.id, start_time, end_time)
        await message.answer("Занятие сохранено")
        await select_day(message)
    else:
        await message.answer("Неверный формат времени")


@bp.on.message(
    EventPayloadContainsRule({"block": "schedule"}),
    EventPayloadContainsRule(
        {"action": "select:time"},
    ),
)
async def select_lesson_type(message: Message):
    payload = json.loads(message.payload)
    user_id = await get_user_id(message.peer_id)
    await update_lesson_storage(
        user_id,
        time_id=payload.get("time"),
    )
    student = await get_student(user_id=user_id)
    group = await student.group
    lesson_types = await get_lesson_types()
    storage = await get_or_create_lesson_storage(user_id)
    if lesson := await find_lesson(
        storage.week.id,
        storage.day.id,
        storage.time.id,
        group.id,
    ):
        await message.answer(
            "В этом слоте есть занятие:\n"
            f"{lesson.day.name} ({lesson.week.name[0].upper()}) "
            f"{lesson.time.start_time} - {lesson.time.end_time}\n"
            f"{lesson.subject.full_name} ({lesson.lesson_type.name[0].upper()})\n"
            f"{lesson.teacher.last_name} {lesson.teacher.first_name[0]}. {lesson.teacher.patronymic[0]}.",
        )
    await message.answer(
        "Выберите тип занятия",
        keyboard=keyboards.lesson_types(lesson_types),
    )
