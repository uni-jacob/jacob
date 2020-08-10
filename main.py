import os

from vkwave.bots import SimpleLongPollBot
from vkwave.bots import TextFilter

bot = SimpleLongPollBot(tokens=os.getenv("VK_TOKEN"), group_id=os.getenv("GROUP_ID"))


@bot.message_handler(TextFilter(["старт", "начать", "start"]))
def handle(_) -> str:
    return "Привет!"


bot.run_forever()
