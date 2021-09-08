import json

from vkbottle import EMPTY_KEYBOARD
from vkbottle.bot import Message

from jacob.services.exceptions import PayloadIsEmptyOrNotFound


async def send_empty_keyboard(message: Message):
    msg_id = await message.answer("...", keyboard=EMPTY_KEYBOARD)
    await message.ctx_api.messages.delete([msg_id], delete_for_all=True)


async def get_previous_payload(message: Message, offset: int) -> dict:
    query = await message.ctx_api.messages.get_by_id([message.id - offset])
    msg = query.items[0]
    try:
        return json.loads(msg.payload)
    except (TypeError, AttributeError):
        raise PayloadIsEmptyOrNotFound(f'Пейлоад в сообщении "{msg.text}" не найден')
