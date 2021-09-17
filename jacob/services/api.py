import json
from typing import Optional

from vkbottle import EMPTY_KEYBOARD
from vkbottle.bot import Message


async def send_empty_keyboard(message: Message):
    """
    Отправляет сообщение с пустой клавиатурой и удаляет его.

    Args:
        message: Объект сообщения
    """
    msg_id = await message.answer("...", keyboard=EMPTY_KEYBOARD)
    await message.ctx_api.messages.delete([msg_id], delete_for_all=True)


async def get_previous_payload(message: Message, key: str) -> Optional[dict]:
    """
    Ищет пейлоад с конкретным ключом в 20 последних сообщениях.

    Args:
        message: Объект сообщения
        key: Искомый ключ

    Returns:
        dict: Пейлоад сообщения
    """
    query = await message.ctx_api.messages.get_history(
        offset=0,
        count=20,
        peer_id=message.peer_id,
        start_message_id=message.id,
    )
    for msg in query.items:
        if msg.payload is not None:
            payload = json.loads(msg.payload)
            if key in payload:
                return payload

    return None
