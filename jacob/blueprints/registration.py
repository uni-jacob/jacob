from vkbottle.bot import Blueprint, Message

from jacob.database.utils.users import set_state
from jacob.services.rules import EventPayloadContainsRule
from jacob.services import keyboards as kb

bp = Blueprint("Group registration")
bp.labeler.auto_rules = [EventPayloadContainsRule({"block": "registration"})]


@bp.on.message(
    EventPayloadContainsRule({"action": "init"}),
)
async def init_registration(message: Message):
    await set_state(message.peer_id, "registration:select_university")
    await message.answer(
        "Выберите или создайте университет",
        keyboard=await kb.list_of_universities(),
    )


@bp.on.message(
    EventPayloadContainsRule({"action": "university:select"}),
)
async def select_university(message: Message):
    ...


@bp.on.message(
    EventPayloadContainsRule({"action": "university:create"}),
)
async def create_university(message: Message):
    await message.answer("Введите название университета")
