import json
import logging

from vkbottle import EMPTY_KEYBOARD
from vkbottle.bot import Message

from jacob.services.exceptions import PayloadIsEmptyOrNotFound


async def send_empty_keyboard(message: Message):
    """
    Отправляет сообщение с пустой клавиатурой и удаляет его
    Args:
        message: Объект сообщения
    """
    msg_id = await message.answer("...", keyboard=EMPTY_KEYBOARD)
    await message.ctx_api.messages.delete([msg_id], delete_for_all=True)


async def get_previous_payload(message: Message, offset: int) -> dict:
    """
    Получает пейлоад предыдущего сообщения по указанному отступу
    Args:
        message: Объект сообщения
        offset: Отступ от последнего сообщения

    Returns:
        dict: Пейлоад сообщения
    """
    query = await message.ctx_api.messages.get_by_id([message.id - offset])
    msg = query.items[0]
    try:
        payload = json.loads(msg.payload)
    except (TypeError, AttributeError):
        raise PayloadIsEmptyOrNotFound(f'Пейлоад в сообщении "{msg.text}" не найден')
    logging.info(f"Пейлоад в сообщении: {payload}")

    return payload
