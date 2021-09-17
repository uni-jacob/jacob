import json
import logging

from vkbottle import EMPTY_KEYBOARD, OrFilter
from vkbottle.bot import Blueprint, Message
from vkbottle.dispatch.rules.bot import VBMLRule

from jacob.database.utils.admins import create_admin, is_admin
from jacob.database.utils.groups import create_group
from jacob.database.utils.states import get_state_name_by_id
from jacob.database.utils.students import create_student
from jacob.database.utils.universities import (
    create_new_university,
    get_university_by_id,
    update_university_abbreviation,
    get_universities,
)
from jacob.database.utils.users import set_state, get_state_of_user, get_user_id
from jacob.services import keyboards as kb
from jacob.services.api import get_previous_payload
from jacob.services.common import generate_abbreviation
from jacob.services.middleware import ChangeSentryUser
from jacob.services.rules import EventPayloadContainsRule, StateRule

bp = Blueprint("Group registration")
bp.labeler.message_view.register_middleware(ChangeSentryUser())


@bp.on.message(
    EventPayloadContainsRule({"block": "registration"}),
    EventPayloadContainsRule({"action": "init"}),
)
async def init_registration(message: Message):
    logging.info("Запущена регистрация новой группы")
    await set_state(message.peer_id, "registration:select_university")
    universities = await get_universities()
    await message.answer(
        "Выберите или создайте университет",
        keyboard=await kb.list_of_universities(universities),
    )


@bp.on.message(
    EventPayloadContainsRule({"block": "registration"}),
    EventPayloadContainsRule({"action": "university:select"}),
)
async def select_university(message: Message):
    payload = json.loads(message.payload)
    university = await get_university_by_id(payload.get("university"))
    logging.info(f"Выбран университет {university.abbreviation}")
    await message.answer(
        f"Выбран университет {university.abbreviation}",
        payload=json.dumps(
            {"university_id": university.id},
        ),
    )
    await start_create_group(message, "select")


@bp.on.message(
    EventPayloadContainsRule({"block": "registration"}),
    EventPayloadContainsRule({"action": "university:create"}),
)
async def create_university(message: Message):
    logging.info("Запущено создание нового университета: Ожидание названия...")
    await set_state(message.peer_id, "registration:ask_university_name")
    await message.answer("Введите название университета", keyboard=kb.cancel())


@bp.on.message(
    EventPayloadContainsRule({"action": "cancel"}),
    StateRule("registration:ask_university_name"),
)
async def cancel_creating_university(message: Message):
    logging.info("Регистрация университета отменена")
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
    logging.info(f"Университет {university_name} создан")
    logging.info(
        f"Вопрос к пользователю - верна ли автоматически созданная аббревиатура: {abbreviation}?"
    )
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
    logging.info("Автоматически созданная аббревиатура верна. Обновление записи в БД.")
    payload = await get_previous_payload(message, 1)
    university_id = payload.get("university_id")
    university = await get_university_by_id(university_id)
    abbreviation = generate_abbreviation(university.name)
    await update_university_abbreviation(university.id, abbreviation)
    await message.answer(
        f"Аббревиатура {abbreviation} сохранена",
        keyboard=EMPTY_KEYBOARD,
    )
    await start_create_group(message, "create")


@bp.on.message(
    EventPayloadContainsRule({"action": "no"}),
    StateRule("registration:confirm_abbreviation"),
)
async def ask_for_abbreviation(message: Message):
    logging.info(
        "Автоматически созданная аббревиатура не верна. Запрос корректной аббревиатуры"
    )
    await set_state(message.peer_id, "registration:ask_for_abbreviation")
    await message.answer("Введите корректную аббревиатуру (до 13 символов)")


@bp.on.message(
    VBMLRule("<abbreviation>"),
    StateRule("registration:ask_for_abbreviation"),
)
async def save_university_abbreviation(message: Message, abbreviation: str):
    logging.info("Получена новая аббревиатура. Обновление записи в БД.")
    payload = await get_previous_payload(message, 3)
    university_id = payload.get("university_id")
    university = await get_university_by_id(university_id)
    await update_university_abbreviation(university.id, abbreviation)
    await message.answer(
        f"Аббревиатура {abbreviation} сохранена",
        keyboard=EMPTY_KEYBOARD,
    )
    await start_create_group(message, "create")


@bp.on.message(
    VBMLRule("<group_name>"),
    OrFilter(
        StateRule("registration:ask_group_name:select"),
        StateRule("registration:ask_group_name:create"),
    ),
)
async def ask_specialty(message: Message, group_name: str):
    logging.info("Запрос названия специальности")
    query = await get_state_name_by_id(await get_state_of_user(message.peer_id))
    ref = query.split(":")[-1]
    await set_state(message.peer_id, f"registration:ask_specialty_name:{ref}")
    await message.answer(
        f"Введите название специальности для группы {group_name}",
        payload=json.dumps({"group_name": group_name}),
    )


async def start_create_group(message: Message, ref: str):
    logging.info("Начато создание новой группы")
    await set_state(message.peer_id, f"registration:ask_group_name:{ref}")
    await message.answer("Введите название группы")


@bp.on.message(
    VBMLRule("<specialty_name>"),
    StateRule("registration:ask_specialty_name:select"),
)
async def save_group_from_selecting(message: Message, specialty_name: str):
    logging.info("Новая группа в существовавшем университете создана")
    university_payload = await get_previous_payload(message, 4)
    await save_group(message, specialty_name, university_payload)


@bp.on.message(
    VBMLRule("<specialty_name>"),
    StateRule("registration:ask_specialty_name:create"),
)
async def save_group_from_creating(message: Message, specialty_name: str):
    logging.info("Новая группа в новом университете создана")
    university_payload = await get_previous_payload(message, 6)
    await save_group(message, specialty_name, university_payload)


async def save_group(message: Message, specialty_name: str, university_payload: dict):
    group_payload = await get_previous_payload(message, 1)
    group_name = group_payload.get("group_name")
    university_id = university_payload.get("university_id")
    group = await create_group(group_name, specialty_name, university_id)
    user_id = await get_user_id(message.peer_id)
    vk_user = await message.ctx_api.users.get([str(message.peer_id)])
    # FIXME: Дублирует запись, если пользователь уже есть в другой группе
    await create_student(user_id, vk_user[0].first_name, vk_user[0].last_name, group.id)
    # FIXME: Падает, если пользователь уже админ другой группы
    await create_admin(user_id, group.id)
    await message.answer("Группа сохранена")
    await set_state(message.peer_id, "main")
    await message.answer(
        "Добро пожаловать!", keyboard=kb.main_menu(await is_admin(user_id))
    )
