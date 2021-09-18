import json
import logging

from vkbottle.bot import Blueprint, Message

from jacob.database.utils.admins import toggle_group_selection
from jacob.database.utils.groups import get_managed_groups
from jacob.database.utils.users import get_user_id
from jacob.services import keyboards as kb
from jacob.services.middleware import ChangeSentryUser
from jacob.services.rules import EventPayloadContainsRule

bp = Blueprint("UpperMenu")
bp.labeler.message_view.register_middleware(ChangeSentryUser())


@bp.on.message(
    EventPayloadContainsRule({"block": "groups"}),
    EventPayloadContainsRule({"action": "show"}),
)
async def show_managed_groups(message: Message):
    logging.info("Открытие меню доступных для управления групп...")
    managed_groups = await get_managed_groups(message.peer_id)
    await message.answer(
        "Выберите активные группы",
        keyboard=await kb.managed_groups(managed_groups),
    )


@bp.on.message(
    EventPayloadContainsRule({"block": "groups"}),
    EventPayloadContainsRule({"action": "select"}),
)
async def toggle_group(message: Message):
    payload = json.loads(message.payload)
    await toggle_group_selection(
        payload.get("group_id"),
        await get_user_id(message.peer_id),
    )
    await show_managed_groups(message)
