import asyncio
import os

from tortoise import Tortoise
from vkbottle import Bot
from vkbottle import Message

import utils
from database.db import Database
from database.models import State
from keyboard import Keyboards
from utils.rules import ButtonRule
from utils.rules import StateRule

bot = Bot(os.environ["VK_TOKEN"])
db = Database(os.environ["DATABASE_URL"])
kbs = Keyboards()


async def init_db():
    await Tortoise.init(
        db_url=os.environ["DATABASE_URL"], modules={"models": ["database.models"]}
    )


@bot.on.message(text="начать", lower=True)
async def start_bot(ans: Message):
    await ans(f"Привет!", keyboard=kbs.main_menu(ans.from_id))


@bot.on.message(ButtonRule("home"))
async def start_bot(ans: Message):
    await ans(f"Главное меню", keyboard=kbs.main_menu(ans.from_id))


@bot.on.message(ButtonRule("call"))
async def open_call(ans: Message):
    user = await utils.get_storage(ans.from_id)
    state = await State.get(description="wait_call_text")
    user.state_id = state.id
    await user.save()
    await ans(
        "Отправьте сообщение к призыву", keyboard=kbs.skip_call_message(),
    )


@bot.on.message(StateRule("wait_call_text"), text="<message>")
async def register_call_message(ans: Message, message: str):
    user = await utils.get_storage(ans.from_id)
    if user is not None:
        state = await State.get(description="main")
        user.text = message
        user.state_id = state.id
        await user.save()
    else:
        return "Access denied."
    await ans(message="Выберите призываемых:", keyboard=kbs.call_interface(ans.from_id))


@bot.on.message(ButtonRule("skip_call_message"))
async def generate_call_kb(ans: Message):
    await ans(message="Выберите призываемых:", keyboard=kbs.call_interface(ans.from_id))


@bot.on.message(ButtonRule("cancel_call"))
async def cancel_call(ans: Message):
    await utils.clear_storage(ans.from_id)
    await ans("Выполнение команды отменено", keyboard=kbs.main_menu(ans.from_id))


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


loop = asyncio.get_event_loop()
loop.run_until_complete(init_db())
bot.run_polling(skip_updates=False)
