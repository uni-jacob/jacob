from vkbottle import EMPTY_KEYBOARD
from vkbottle.bot import Message


async def send_empty_keyboard(message: Message):
    msg_id = await message.answer("...", keyboard=EMPTY_KEYBOARD)
    await message.ctx_api.messages.delete([msg_id], delete_for_all=True)
