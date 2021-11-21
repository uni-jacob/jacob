import json
import re

from vkbottle import EMPTY_KEYBOARD
from vkbottle.bot import Blueprint, Message

from jacob.database.utils.classrooms import get_classrooms
from jacob.database.utils.schedule.classroom import update_or_create_classroom
from jacob.database.utils.schedule.days import get_days
from jacob.database.utils.schedule.lesson_types import get_lesson_types
from jacob.database.utils.schedule.subjects import get_subjects, update_subject
from jacob.database.utils.schedule.teachers import (
    create_new_teacher,
    get_teachers,
)
from jacob.database.utils.schedule.timetable import (
    create_lesson_time,
    get_timetable,
)
from jacob.database.utils.students import get_student
from jacob.database.utils.universities import find_university_of_user
from jacob.database.utils.users import get_user_id, set_state
from jacob.services import keyboards
from jacob.services.api import get_previous_payload
from jacob.services.common import vbml_rule
from jacob.services.keyboards.pagination.teachers import TeachersPagination
from jacob.services.middleware import ChangeSentryUser
from jacob.services.rules import EventPayloadContainsRule, StateRule

bp = Blueprint("Schedule:edit")
bp.labeler.message_view.register_middleware(ChangeSentryUser())
vbml_rule = vbml_rule(bp)


@bp.on.message(
    EventPayloadContainsRule({"block": "schedule"}),
    EventPayloadContainsRule(
        {"action": "select:week"},
    ),
)
async def select_week(message: Message):
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
    await set_state(message.peer_id, "schedule:edit:select_time")
    university = await find_university_of_user(await get_user_id(message.peer_id))
    timetable = await get_timetable(university.id)
    await message.answer(
        "Выберите время занятия", keyboard=keyboards.timetable(timetable)
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
        {"action": "select:lesson"},
    ),
)
async def select_lesson_type(message: Message):
    lesson_types = await get_lesson_types()
    await message.answer(
        "Выберите тип занятия", keyboard=keyboards.lesson_types(lesson_types)
    )


@bp.on.message(
    EventPayloadContainsRule({"block": "schedule"}),
    EventPayloadContainsRule(
        {"action": "select:lesson_type"},
    ),
)
async def select_teacher(message: Message):
    await set_state(message.peer_id, "schedule:edit:select_teacher")
    university = await find_university_of_user(await get_user_id(message.peer_id))
    teachers = await get_teachers(university.id)
    await message.answer(
        "Выберите преподавателя",
        keyboard=TeachersPagination(teachers, "schedule").function_menu(),
    )


@bp.on.message(
    EventPayloadContainsRule({"block": "schedule"}),
    EventPayloadContainsRule(
        {"action": "create:teacher"},
    ),
)
async def create_teacher(message: Message):
    await set_state(message.peer_id, "schedule:create_teacher")
    await message.answer(
        "Введите полное имя преподавателя (ФИО) через пробел", keyboard=EMPTY_KEYBOARD
    )


@bp.on.message(
    vbml_rule("<last_name> <first_name> <patronymic>"),
    StateRule("schedule:create_teacher"),
)
async def save_teacher(
    message: Message,
    last_name: str,
    first_name: str,
    patronymic: str,
):
    university = await find_university_of_user(await get_user_id(message.peer_id))
    await create_new_teacher(
        university.id,
        last_name,
        first_name,
        patronymic,
    )
    await message.answer("Преподаватель сохранён")
    await select_teacher(message)


@bp.on.message(
    EventPayloadContainsRule({"block": "schedule"}),
    EventPayloadContainsRule(
        {"action": "half"},
    ),
)
async def select_half(message: Message):
    payload = json.loads(message.payload)
    university = await find_university_of_user(await get_user_id(message.peer_id))
    teachers = await get_teachers(university.id)
    await message.answer(
        "Выберите преподавателя",
        keyboard=TeachersPagination(teachers, "schedule").submenu(payload.get("half")),
    )


@bp.on.message(
    EventPayloadContainsRule({"block": "schedule"}),
    EventPayloadContainsRule(
        {"action": "select_letter"},
    ),
)
async def select_letter(message: Message):
    payload = json.loads(message.payload)
    university = await find_university_of_user(await get_user_id(message.peer_id))
    teachers = await get_teachers(university.id)
    await message.answer(
        "Выберите преподавателя",
        keyboard=TeachersPagination(teachers, "schedule").entries_menu(
            payload.get("letter"),
        ),
    )


@bp.on.message(
    EventPayloadContainsRule({"block": "schedule"}),
    EventPayloadContainsRule(
        {"action": "select_personality"},
    ),
)
async def select_subject(message: Message):
    user_id = await get_user_id(message.peer_id)
    student = await get_student(user_id=user_id)
    group = await student.group
    subjects = await get_subjects(group.id)
    await message.answer("Выберите предмет", keyboard=keyboards.subjects(subjects))


@bp.on.message(
    EventPayloadContainsRule({"block": "schedule"}),
    EventPayloadContainsRule({"action": "create:subject"}),
)
async def create_subject(message: Message):
    await set_state(message.peer_id, "schedule:create_subject")
    await message.answer("Введите название предмета", keyboard=EMPTY_KEYBOARD)


@bp.on.message(
    vbml_rule("<name>"),
    StateRule("schedule:create_subject"),
)
async def enter_subject_abbreviation(message: Message, name: str):
    from jacob.database.utils.schedule.subjects import create_subject

    await set_state(message.peer_id, "schedule:enter_subject_abbreviation")
    user_id = await get_user_id(message.from_id)
    student = await get_student(user_id=user_id)
    group = await student.group
    subj = await create_subject(group=group, full_name=name)
    await message.answer(
        f"Введите аббревиатуру предмета {name}",
        payload=json.dumps({"subject_id": subj.id}),
        keyboard=EMPTY_KEYBOARD,
    )


@bp.on.message(
    vbml_rule("<abbr>"),
    StateRule("schedule:enter_subject_abbreviation"),
)
async def save_subject(message: Message, abbr: str):
    payload = await get_previous_payload(message, "subject_id")
    user_id = await get_user_id(message.peer_id)
    student = await get_student(user_id=user_id)
    group = await student.group
    subjects = await get_subjects(group.id)

    await update_subject(payload.get("subject_id"), abbreviation=abbr)
    await set_state(message.peer_id, "schedule:main")
    await message.answer(f"Предмет сохранен", keyboard=keyboards.subjects(subjects))


@bp.on.message(
    EventPayloadContainsRule({"block": "schedule"}),
    EventPayloadContainsRule({"action": "select:subject"}),
)
async def select_classroom(message: Message):
    user_id = await get_user_id(message.peer_id)
    university = await find_university_of_user(user_id)
    classrooms = await get_classrooms(university.id)
    await message.answer(
        "Выберите аудиторию", keyboard=keyboards.classrooms(classrooms)
    )


@bp.on.message(
    EventPayloadContainsRule({"block": "schedule"}),
    EventPayloadContainsRule({"action": "create:classroom"}),
)
async def init_create_classroom(message: Message):
    await set_state(message.peer_id, "schedule:enter_building_number")
    await message.answer("Введите номер корпуса", keyboard=EMPTY_KEYBOARD)


@bp.on.message(
    vbml_rule("<building>"),
    StateRule("schedule:enter_building_number"),
)
async def save_building_number(message: Message, building: int):
    user_id = await get_user_id(message.peer_id)
    university = await find_university_of_user(user_id)
    classroom = await update_or_create_classroom(
        building=building, university=university
    )

    await set_state(message.peer_id, "schedule:enter_classroom_number")
    await message.answer(
        "Введите номер аудитории",
        payload=json.dumps({"classroom_id": classroom.id}),
    )


@bp.on.message(
    vbml_rule("<classroom>"),
    StateRule("schedule:enter_classroom_number"),
)
async def save_classroom(message: Message, classroom: str):
    payload = await get_previous_payload(message, "classroom_id")
    await update_or_create_classroom(
        id=payload.get("classroom_id"), class_name=classroom
    )

    user_id = await get_user_id(message.peer_id)
    university = await find_university_of_user(user_id)
    classrooms = await get_classrooms(university.id)

    await set_state(message.peer_id, "schedule:main")
    await message.answer(
        "Аудитория сохранена!",
        keyboard=keyboards.classrooms(classrooms),
    )


@bp.on.message(
    EventPayloadContainsRule({"block": "schedule"}),
    EventPayloadContainsRule({"action": "select:classroom"}),
)
async def select_classroom(message: Message):
    await message.answer("Занятие сохранено!")
