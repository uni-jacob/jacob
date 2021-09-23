import re

from vkbottle import EMPTY_KEYBOARD
from vkbottle.bot import Blueprint, Message

from jacob.database.utils.admins import is_admin
from jacob.database.utils.schedule.days import get_days
from jacob.database.utils.schedule.timetable import (
    create_lesson_time,
    get_timetable,
)
from jacob.database.utils.schedule.weeks import get_weeks
from jacob.database.utils.universities import find_university_of_user
from jacob.database.utils.users import get_user_id, set_state
from jacob.services import keyboards as kb
from jacob.services.common import vbml_rule
from jacob.services.middleware import ChangeSentryUser
from jacob.services.rules import EventPayloadContainsRule, StateRule

bp = Blueprint("Schedule")
bp.labeler.message_view.register_middleware(ChangeSentryUser())
vbml_rule = vbml_rule(bp)


@bp.on.message(
    EventPayloadContainsRule({"block": "schedule"}),
    EventPayloadContainsRule(
        {"action": "init"},
    ),
)
async def open_schedule(message: Message):
    await set_state(message.peer_id, "schedule:main")
    is_admin_ = await is_admin(await get_user_id(message.peer_id))
    await message.answer("Блок Расписание", keyboard=kb.schedule_main(is_admin_))


@bp.on.message(
    EventPayloadContainsRule({"block": "schedule"}),
    EventPayloadContainsRule(
        {"action": "edit"},
    ),
)
async def init_editing_schedule(message: Message):
    await set_state(message.peer_id, "schedule:edit:select_week")
    weeks = await get_weeks()
    await message.answer("Выбор недели", keyboard=kb.weeks(weeks))


@bp.on.message(
    EventPayloadContainsRule({"block": "schedule"}),
    EventPayloadContainsRule(
        {"action": "select:week"},
    ),
)
async def select_week(message: Message):
    await set_state(message.peer_id, "schedule:edit:select_day")
    days = await get_days()
    await message.answer("Выберите день", keyboard=kb.days(days))


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
    await message.answer("Выберите время занятия", keyboard=kb.timetable(timetable))


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
