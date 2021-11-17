from vkbottle.bot import Blueprint, Message

from jacob.database.utils.admins import is_admin
from jacob.database.utils.schedule.weeks import get_weeks
from jacob.database.utils.users import get_user_id, set_state
from jacob.services import keyboards
from jacob.services.common import vbml_rule
from jacob.services.middleware import ChangeSentryUser
from jacob.services.rules import EventPayloadContainsRule

bp = Blueprint("Schedule:")
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
    await message.answer("Блок Расписание", keyboard=keyboards.schedule_main(is_admin_))


@bp.on.message(
    EventPayloadContainsRule({"block": "schedule"}),
    EventPayloadContainsRule(
        {"action": "edit"},
    ),
)
async def init_editing_schedule(message: Message):
    await set_state(message.peer_id, "schedule:edit:select_week")
    weeks = await get_weeks()
    await message.answer("Выбор недели", keyboard=keyboards.weeks(weeks))
