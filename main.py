import os

from vkwave.bots import SimpleLongPollBot

bot = SimpleLongPollBot(tokens=os.getenv("VK_TOKEN"), group_id=os.getenv("GROUP_ID"))


@bot.message_handler()
def handle(_) -> str:
    return f"Hello world!"


bot.run_forever()
