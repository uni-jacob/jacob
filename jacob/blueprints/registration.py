from vkbottle.bot import Blueprint, Message

from jacob.services.rules import EventPayloadContainsRule

bp = Blueprint("Group registration")
bp.labeler.auto_rules = [EventPayloadContainsRule({"block": "registration"})]


@bp.on.message(
    EventPayloadContainsRule({"action": "init"}),
)
async def init_registration(message: Message):
    # TODO: Смена стейта на invite:select_university
    await message.answer(
        "Выберите или создайте университет",
    )
