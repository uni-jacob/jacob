from vkbottle.bot import Blueprint
from vkbottle_types.events import GroupEventType, MessageEvent

from jacob.services.rules import PayloadContainsRule

bp = Blueprint("Group registration")
bp.labeler.auto_rules = [PayloadContainsRule({"block": "registration"})]


@bp.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadContainsRule({"action": "init"}),
)
async def init_registration(message: MessageEvent):
    await message.ctx_api.messages.send_message_event_answer(
        event_id=message.object.event_id,
        peer_id=message.object.peer_id,
        user_id=message.object.user_id,
        event_data='{"type": "show_snackbar", "text": "Работает!"}',
    )
