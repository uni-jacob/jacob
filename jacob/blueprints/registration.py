from vkbottle.bot import Blueprint, Message
from vkbottle.dispatch.rules.bot import VBMLRule

from jacob.database.utils.users import set_state
from jacob.services import keyboards as kb
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
    ...


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
    await message.answer(f"Университет {university_name} создан")
