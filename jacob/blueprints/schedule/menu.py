from vkbottle.bot import Blueprint, Message

from jacob.database.utils.schedule.weeks import get_weeks
from jacob.database.utils.users import set_state
from jacob.services import keyboards
from jacob.services.common import vbml_rule
from jacob.services.middleware import ChangeSentryUser
from jacob.services.rules import EventPayloadContainsRule

bp = Blueprint("Schedule:menu")
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
    weeks = await get_weeks()
    await message.answer("Выбор недели", keyboard=keyboards.weeks(weeks))
