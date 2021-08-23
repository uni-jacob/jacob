from vkbottle.bot import Blueprint, Message
from vkbottle.tools.dev_tools.keyboard import EMPTY_KEYBOARD

from jacob.services.rules import EventPayloadContainsRule

bp = Blueprint("Group registration")
bp.labeler.auto_rules = [EventPayloadContainsRule({"block": "registration"})]


@bp.on.message(
    EventPayloadContainsRule({"action": "init"}),
)
async def init_registration(message: Message):
    await message.answer(
        "Выберите или создайте университет",
    )


@bp.on.message(
    EventPayloadContainsRule({"action": "enter_invite"}),
)
async def enter_invite_code(message: Message):
    await message.answer(
        message="Введите код приглашения",
        keyboard=EMPTY_KEYBOARD,  # TODO: Кнопка отмены
    )
