import logging
import os

from vkwave.bots import SimpleBotEvent
from vkwave.bots import SimpleLongPollBot
from vkwave.bots import TextFilter

from services import keyboard as kbs

logging.basicConfig(level=logging.DEBUG)
bot = SimpleLongPollBot(tokens=os.getenv("VK_TOKEN"), group_id=os.getenv("GROUP_ID"))


@bot.message_handler(TextFilter(["старт", "начать", "start", "привет", "hi", "hello"]))
async def start(ans: SimpleBotEvent):
    await ans.answer(
        "Привет!", keyboard=kbs.main_menu(ans.object.object.message.peer_id)
    )


bot.run_forever()
