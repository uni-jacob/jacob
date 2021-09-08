import json

from vkbottle import EMPTY_KEYBOARD
from vkbottle.bot import Message


async def send_empty_keyboard(message: Message):
    msg_id = await message.answer("...", keyboard=EMPTY_KEYBOARD)
    await message.ctx_api.messages.delete([msg_id], delete_for_all=True)


async def get_previous_payload(message: Message, offset: int) -> dict:
    query = await message.ctx_api.messages.get_by_id([message.id - offset])
    return json.loads(query.items[0].payload)
