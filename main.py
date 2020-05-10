import os

from vkbottle import Bot
from vkbottle import Message

from keyboard import Keyboards
from utils.rules import ButtonRule

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


@bot.on.message(ButtonRule("settings"))
async def open_mailings(ans: Message):
    await ans("Здесь будут настройки...")


@bot.on.message(ButtonRule("web"))
async def open_mailings(ans: Message):
    await ans("Здесь будет доступ к вебу...")


bot.run_polling(skip_updates=False)
