import asyncio
import json
import os
import random

from tortoise import Tortoise
from vkbottle import Bot
from vkbottle import Message
from vkbottle.rule import VBMLRule
from vkbottle.rule import filters
from vkbottle.rule import AttachmentRule

from database import Database
from database import utils
from database.models import Administrator
from database.models import Chat
from database.models import State
from keyboard import Keyboards
from utils import call
from utils import media
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
    await ans(f"Привет!", keyboard=await kbs.main_menu(ans.from_id))


@bot.on.message(ButtonRule("home"))
async def start_bot(ans: Message):
    await ans(f"Главное меню", keyboard=await kbs.main_menu(ans.from_id))


@bot.on.message(ButtonRule("call"))
async def open_call(ans: Message):
    user = await utils.get_storage(ans.from_id)
    state = await State.get(description="wait_call_text")
    user.state_id = state.id
    await user.save()
    await ans(
        "Отправьте сообщение к призыву", keyboard=kbs.skip_call_message(),
    )


@bot.on.message(ButtonRule("cancel_call"))
async def cancel_call(ans: Message):
    await utils.clear_storage(ans.from_id)
    await ans("Выполнение команды отменено", keyboard=kbs.main_menu(ans.from_id))


@bot.on.message(
    StateRule("wait_call_text"),
    filters.or_filter(AttachmentRule(), VBMLRule("<message>")),
)
async def register_call_message(ans: Message):
    user = await utils.get_storage(ans.from_id)
    if ans.attachments:
        attaches = await media.load_attachments(bot, ans.attachments, ans.from_id)
        user.attaches = attaches
        await user.save()
    if user is not None:
        state = await State.get(description="main")
        user.text = ans.text
        user.state_id = state.id
        await user.save()
    else:
        return "Access denied."
    await ans(message="Выберите призываемых:", keyboard=kbs.call_interface(ans.from_id))


@bot.on.message(ButtonRule("skip_call_message"))
async def generate_call_kb(ans: Message):
    await ans(message="Выберите призываемых:", keyboard=kbs.call_interface(ans.from_id))


@bot.on.message(ButtonRule("letter"))
async def generate_students_kb(ans: Message):
    payload = json.loads(ans.payload)
    await ans(
        f"Список студентов на букву \"{payload['value']}\"",
        keyboard=kbs.list_of_students(payload["value"], ans.from_id),
    )


@bot.on.message(ButtonRule("student"))
async def edit_call_list(ans: Message):
    payload = json.loads(ans.payload)
    user = await utils.get_storage(ans.from_id)
    if user.selected_students is None:
        user.selected_students = ""
    students = [i for i in user.selected_students.split(",") if i]
    if str(payload["student_id"]) not in students:
        students.append(str(payload["student_id"]))
        user.selected_students = ",".join(students)
        await user.save()
        await ans(f"{payload['name']} добавлен к списку призывемых")
    else:
        students.remove(str(payload["student_id"]))
        user.selected_students = ",".join(students)
        await user.save()
        await ans(f"{payload['name']} убран из списка призывемых")


@bot.on.message(ButtonRule("save_selected"))
async def save_call(ans: Message):
    user = await utils.get_storage(ans.from_id)
    state = await State.get(description="confirm_call")
    user.state_id = state.id
    await user.save()
    chat_id = user.current_chat
    chat = await Chat.get(id=chat_id)
    chat_text = "основную" if chat.chat_type else "тестовую"
    message = await call.generate_message(ans.from_id)
    attachments = user.attaches
    await ans(f"Это сообщение будет отправлено в {chat_text} беседу:")
    await ans(
        message=message,
        attachment=attachments,
        keyboard=kbs.call_prompt(user.names_usage, chat.chat_type),
    )


@bot.on.message(StateRule("confirm_call"), ButtonRule("confirm"))
async def confirm_call(ans: Message):
    user = await utils.get_storage(ans.from_id)
    state = await State.get(description="main")
    user.state_id = state.id
    await user.save()
    message = await call.generate_message(ans.from_id)
    attachments = user.attaches
    chat_id = user.current_chat
    chat = await Chat.get(id=chat_id)
    await bot.api.messages.send(
        random_id=random.getrandbits(64),
        peer_id=chat.chat_id,
        message=message,
        attachment=attachments,
    )
    await utils.clear_storage(ans.from_id)
    await ans("Сообщение отправлено", keyboard=kbs.main_menu(ans.from_id))


@bot.on.message(StateRule("confirm_call"), ButtonRule("deny"))
async def deny_call(ans: Message):
    user = await utils.get_storage(ans.from_id)
    state = await State.get(description="main")
    user.state_id = state.id
    await user.save()
    await utils.clear_storage(ans.from_id)
    await ans("Выполнение команды отменено", keyboard=kbs.main_menu(ans.from_id))


@bot.on.message(StateRule("confirm_call"), ButtonRule("names_usage"))
async def edit_names_usage(ans: Message):
    user = await utils.get_storage(ans.from_id)
    user.names_usage = not user.names_usage
    await user.save()
    await save_call(ans)


@bot.on.message(StateRule("confirm_call"), ButtonRule("chat_config"))
async def edit_chat(ans: Message):
    user = await utils.get_storage(ans.from_id)
    chat_id = user.current_chat
    chat = await Chat.get(id=chat_id)
    chat_type = chat.chat_type
    chat_type = 0 if chat_type else 1
    admin = await Administrator.get(vk_id=ans.from_id)
    print(admin.group_id)
    chat = await Chat.get_or_none(
        alma_mater=admin.alma_mater_id, group=admin.group_id, chat_type=chat_type,
    )
    if chat is not None:
        user.current_chat = chat.id
        await user.save()
        await save_call(ans)
    else:
        chat_text = "Основной" if chat_type else "Тестовый"
        await ans(f"{chat_text} чат не настроен")


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
    await ans("Настройки бота", keyboard=kbs.settings())


@bot.on.message(ButtonRule("web"))
async def open_mailings(ans: Message):
    await ans("Здесь будет доступ к вебу...")


loop = asyncio.get_event_loop()
loop.run_until_complete(init_db())
bot.run_polling(skip_updates=False)
