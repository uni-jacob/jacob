import os

from vkbottle import Bot
from vkbottle import Message
from vkbottle.rule import PayloadRule

from keyboard import Keyboards

bot = Bot(os.environ["VK_TOKEN"])
kbs = Keyboards()


@bot.on.message(text="начать", lower=True)
async def start_bot(ans: Message):
    await ans("Привет", keyboard=kbs.main_menu(ans.from_id))


@bot.on.message(PayloadRule({"button": "call"}, mode=2))
async def start_call(ans: Message):
    await ans(f"Здесь будет призыв...")


bot.run_polling(skip_updates=False)
