import pytest
from vkbottle import BaseMiddleware
from vkbottle.bot import Message

from jacob.blueprints.registration import init_registration
from jacob.main import bot


class TestMiddleware(BaseMiddleware):
    def __init__(self, handler):
        self.handler = handler

    def post(self, event, view, handle_responses, handlers):
        assert False


@pytest.mark.asyncio
async def test_init_registration():
    event = Message()
    event.payload = {"block": "registration", "action": "init"}
    bot.labeler.message_view.register_middleware(TestMiddleware(init_registration))
    await bot.router.route(event, bot.api)
