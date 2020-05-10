import os

from vkbottle import Bot
from vkbottle import Message
from utils.rules import ButtonRule

from keyboard import Keyboards

bot = Bot(os.environ["VK_TOKEN"])
kbs = Keyboards()


@bot.on.message(text="начать", lower=True)
async def start_bot(ans: Message):
    await ans("Привет", keyboard=kbs.main_menu(ans.from_id))


@bot.on.message(ButtonRule("call"))
async def open_call(ans: Message):
    await ans("Здесь будет призыв...")


@bot.on.message(ButtonRule("finances"))
async def open_finances(ans: Message):
    await ans("Здесь будут финансы...")


@bot.on.message(ButtonRule("schedule"))
async def open_schedule(ans: Message):
    await ans("Здесь будет расписание...")


@bot.on.message(ButtonRule("mailings"))
async def open_mailings(ans: Message):
    await ans("Здесь будут рассылки...")


bot.run_polling(skip_updates=False)
