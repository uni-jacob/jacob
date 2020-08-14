import logging
import os

from vkwave.bots import SimpleBotEvent
from vkwave.bots import SimpleLongPollBot
from vkwave.bots import TextFilter

from blueprints import call
from blueprints import preferences
from services import keyboard as kbs
from services.filters import PLFilter

logging.basicConfig(level=logging.DEBUG)
bot = SimpleLongPollBot(tokens=os.getenv("VK_TOKEN"), group_id=os.getenv("GROUP_ID"))
bot.dispatcher.add_router(call.call_router)
bot.dispatcher.add_router(preferences.preferences_router)


@bot.message_handler(
    TextFilter(["старт", "начать", "start", "привет", "hi", "hello"])
    | PLFilter({"button": "main_menu"})
)
async def start(ans: SimpleBotEvent):
    await ans.answer(
        "Привет!", keyboard=kbs.main.main_menu(ans.object.object.message.peer_id)
    )


bot.run_forever()
