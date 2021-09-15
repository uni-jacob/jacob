import logging

from vkbottle.bot import Blueprint, Message

from jacob.database.utils.groups import get_managed_groups
from jacob.services.middleware import ChangeSentryUser
from jacob.services.rules import EventPayloadContainsRule
from jacob.services import keyboards as kb

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
        "Выберите активные группы", keyboard=await kb.managed_groups(managed_groups)
    )
