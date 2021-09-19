from vkbottle.bot import Blueprint, Message

from jacob.services.middleware import ChangeSentryUser
from jacob.services.rules import EventPayloadContainsRule

bp = Blueprint("Schedule")
bp.labeler.message_view.register_middleware(ChangeSentryUser())


@bp.on.message(
    EventPayloadContainsRule({"block": "schedule"}),
    EventPayloadContainsRule(
        {"action": "init"},
    ),
)
async def open_schedule(message: Message):
    await message.answer("Блок Расписание")
