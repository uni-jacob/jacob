import os

from vkbottle import Bot
from vkbottle import Message

from keyboard import Keyboards

bot = Bot(os.environ["VK_TOKEN"])
kbs = Keyboards()


@bot.on.message(text="начать", lower=True)
async def start_bot(ans: Message):
    await ans("Привет", keyboard=kbs.main_menu())


bot.run_polling(skip_updates=False)
