import json

from vkbottle import EMPTY_KEYBOARD
from vkbottle.bot import Blueprint, Message
from vkbottle.dispatch.rules.bot import VBMLRule

from jacob.database.utils.groups import create_group
from jacob.database.utils.universities import (
    create_new_university,
    get_university_by_id,
    update_university_abbreviation,
)
from jacob.database.utils.users import set_state
from jacob.services import keyboards as kb
from jacob.services.api import get_previous_payload
from jacob.services.common import generate_abbreviation
from jacob.services.rules import EventPayloadContainsRule, StateRule

bp = Blueprint("Group registration")


@bp.on.message(
    EventPayloadContainsRule({"block": "registration"}),
    EventPayloadContainsRule({"action": "init"}),
)
async def init_registration(message: Message):
    await set_state(message.peer_id, "registration:select_university")
    await message.answer(
        "Выберите или создайте университет",
        keyboard=await kb.list_of_universities(),
    )


@bp.on.message(
    EventPayloadContainsRule({"block": "registration"}),
    EventPayloadContainsRule({"action": "university:select"}),
)
async def select_university(message: Message):
    payload = json.loads(message.payload)
    university = await get_university_by_id(payload.get("university"))
    await set_state(message.peer_id, "registration:ask_group_name")
    await message.answer(
        f"Выбран университет {university.abbreviation}",
        payload=json.dumps(
            {"university_id": university.id},
        ),
    )
    await message.answer("Введите название группы")


@bp.on.message(
    EventPayloadContainsRule({"block": "registration"}),
    EventPayloadContainsRule({"action": "university:create"}),
)
async def create_university(message: Message):
    await set_state(message.peer_id, "registration:ask_university_name")
    await message.answer("Введите название университета", keyboard=kb.cancel())


@bp.on.message(
    EventPayloadContainsRule({"action": "cancel"}),
    StateRule("registration:ask_university_name"),
)
async def cancel_creating_university(message: Message):
    await init_registration(message)


@bp.on.message(
    VBMLRule("<university_name>"),
    StateRule("registration:ask_university_name"),
)
async def save_university(message: Message, university_name: str):
    abbreviation = generate_abbreviation(university_name)
    await set_state(message.peer_id, "registration:confirm_abbreviation")
    university = await create_new_university(university_name)
    await message.answer(f"Университет {university_name} создан")
    await message.answer(
        f"Аббревиатура {abbreviation} верна?",
        keyboard=kb.yes_no(),
        payload=json.dumps({"university_id": university.id}),
    )


@bp.on.message(
    EventPayloadContainsRule({"action": "yes"}),
    StateRule("registration:confirm_abbreviation"),
)
async def save_generated_abbreviation(message: Message):
    payload = await get_previous_payload(message, 1)
    university_id = payload.get("university_id")
    university = await get_university_by_id(university_id)
    abbreviation = generate_abbreviation(university.name)
    await update_university_abbreviation(university.id, abbreviation)
    await message.answer(
        f"Аббревиатура {abbreviation} сохранена",
        keyboard=EMPTY_KEYBOARD,
    )


@bp.on.message(
    EventPayloadContainsRule({"action": "no"}),
    StateRule("registration:confirm_abbreviation"),
)
async def ask_for_abbreviation(message: Message):
    await set_state(message.peer_id, "registration:ask_for_abbreviation")
    await message.answer("Введите корректную аббревиатуру (до 13 символов)")


@bp.on.message(
    VBMLRule("<abbreviation>"),
    StateRule("registration:ask_for_abbreviation"),
)
async def save_university_abbreviation(message: Message, abbreviation: str):
    payload = await get_previous_payload(message, 3)
    university_id = payload.get("university_id")
    university = await get_university_by_id(university_id)
    await update_university_abbreviation(university.id, abbreviation)
    await message.answer(
        f"Аббревиатура {abbreviation} сохранена",
        keyboard=EMPTY_KEYBOARD,
    )


@bp.on.message(
    VBMLRule("<group_name>"),
    StateRule("registration:ask_group_name"),
)
async def ask_specialty(message: Message, group_name: str):
    await set_state(message.peer_id, "registration:ask_specialty_name")
    await message.answer(
        f"Введите название специальности для группы {group_name}",
        payload=json.dumps({"group_name": group_name}),
    )


@bp.on.message(
    VBMLRule("<specialty_name>"),
    StateRule("registration:ask_specialty_name"),
)
async def save_group(message: Message, specialty_name: str):
    group_payload = await get_previous_payload(message, 1)
    university_payload = await get_previous_payload(message, 4)
    group_name = group_payload.get("group_name")
    university_id = university_payload.get("university_id")
    await create_group(group_name, specialty_name, university_id)
    await message.answer("Группа сохранена")
