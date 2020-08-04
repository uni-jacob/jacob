import os

from vkbottle import Bot
from vkbottle import Message

bot = Bot(os.getenv("VK_TOKEN"))


@bot.on.message(text=["начать", "привет", "старт", "start"])
async def start(ans: Message):
    await ans("Привет")


bot.run_polling(skip_updates=False)
