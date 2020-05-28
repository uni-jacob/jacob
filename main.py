import asyncio
import json
import os
import random

from tortoise import Tortoise
from vkbottle import Bot
from vkbottle import Message
from vkbottle.rule import CommandRule
from vkbottle.rule import AttachmentRule
from vkbottle.rule import VBMLRule
from vkbottle.rule import filters

from database import Database
from database import utils
from database.models import Administrator
from database.models import CachedChat
from database.models import Chat
from database.models import State
from database.models import Student
from keyboard import Keyboards
from utils import call
from utils import media
from utils.filters import NotFilter
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


@bot.on.chat_invite()
async def invite_to_chat(ans: Message):
    await CachedChat.get_or_create(chat_id=ans.peer_id)
    await ans(
        "Привет всем! Я - Якоб, универсальный бот - помощник. Список моих команд "
        "можно получить, отправив /help"
    )


@bot.on.chat_message(CommandRule("help"))
async def commands_list(ans: Message):
    with open("commands.txt", "r") as f:
        commands = f.readlines()
    await ans("\n".join(commands))


@bot.on.chat_message(CommandRule("tr"))
async def transliterate(ans: Message):
    for msg in ans.fwd_messages:
        await ans(media.translate_string(msg.text))
    if msg := ans.reply_message:
        await ans(media.translate_string(msg.text))


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
    await ans("Выполнение команды отменено", keyboard=await kbs.main_menu(ans.from_id))


@bot.on.message(
    filters.and_filter(
        StateRule("wait_call_text"),
        filters.or_filter(AttachmentRule(), VBMLRule("<message>")),
        NotFilter(ButtonRule("skip_call_message")),
    ),
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
    await ans(
        message="Выберите призываемых:", keyboard=await kbs.call_interface(ans.from_id)
    )


@bot.on.message(ButtonRule("skip_call_message"))
async def generate_call_kb(ans: Message):
    user = await utils.get_storage(ans.from_id)
    if user is not None:
        state = await State.get(description="main")
        user.state_id = state.id
        await user.save()
    await ans(
        message="Выберите призываемых:", keyboard=await kbs.call_interface(ans.from_id)
    )


@bot.on.message(ButtonRule("letter"))
async def generate_students_kb(ans: Message):
    payload = json.loads(ans.payload)
    await ans(
        f"Список студентов на букву \"{payload['value']}\"",
        keyboard=await kbs.list_of_students(payload["value"], ans.from_id),
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
    student = await Student.get(vk_id=ans.from_id)
    user = await utils.get_storage(ans.from_id)
    state = await State.get(description="confirm_call")
    user.state_id = state.id
    await user.save()
    chat_type = user.current_chat
    chat = await Chat.get(
        chat_type=chat_type, alma_mater=student.alma_mater_id, group=student.group_id,
    )
    chat_text = "основную" if chat.chat_type else "тестовую"
    message = await call.generate_message(ans.from_id)
    attachments = user.attaches
    await ans(f"Это сообщение будет отправлено в {chat_text} беседу:")
    await ans(
        message=message,
        attachment=attachments,
        keyboard=kbs.call_prompt(user.names_usage, chat.chat_type),
    )


@bot.on.message(ButtonRule("call_all"))
async def call_all_of_them(ans: Message):
    user = await utils.get_storage(ans.from_id)
    students = await db.get_active_students(ans.from_id)
    called = []
    for student in students:
        called.append(str(student["id"]))
    user.selected_students = ",".join(called)
    await user.save()
    await save_call(ans)


@bot.on.message(StateRule("confirm_call"), ButtonRule("confirm"))
async def confirm_call(ans: Message):
    student = await Student.get(vk_id=ans.from_id)
    user = await utils.get_storage(ans.from_id)
    state = await State.get(description="main")
    user.state_id = state.id
    await user.save()
    message = await call.generate_message(ans.from_id)
    attachments = user.attaches
    chat_type = user.current_chat
    chat = await Chat.get(
        chat_type=chat_type, alma_mater=student.alma_mater_id, group=student.group_id,
    )
    await bot.api.messages.send(
        random_id=random.getrandbits(64),
        peer_id=chat.chat_id,
        message=message,
        attachment=attachments,
    )
    await utils.clear_storage(ans.from_id)
    await ans("Сообщение отправлено", keyboard=await kbs.main_menu(ans.from_id))


@bot.on.message(StateRule("confirm_call"), ButtonRule("deny"))
async def deny_call(ans: Message):
    user = await utils.get_storage(ans.from_id)
    state = await State.get(description="main")
    user.state_id = state.id
    await user.save()
    await utils.clear_storage(ans.from_id)
    await ans("Выполнение команды отменено", keyboard=await kbs.main_menu(ans.from_id))


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


@bot.on.message(ButtonRule("admin_settings"))
async def open_chat_settings(ans: Message):
    user = await utils.get_storage(ans.from_id)
    chat_id = user.current_chat
    chat = await Chat.get(id=chat_id)
    await ans(
        "Настройки администратора",
        keyboard=kbs.admin_settings(user.names_usage, chat.chat_type),
    )


@bot.on.message(ButtonRule("group_settings"))
async def open_group_settings(ans: Message):
    await ans("Настроенные чаты", keyboard=await kbs.group_settings(ans.from_id))


@bot.on.message(ButtonRule("configure_chat"))
async def configure_chat(ans: Message):
    payload = json.loads(ans.payload)
    payload.pop("button")
    chats = await bot.api.messages.get_conversations_by_id(
        peer_ids=payload["chat_id"], group_id=bot.group_id
    )
    if chat := chats.items:
        title = chat[0].chat_settings.title
        msg = ""
    else:
        title = "???"
        msg = (
            "Бот не является администратором в этом чате. Это может помешать "
            "его нормальной работе"
        )
    await ans(
        f"Настройки чата {title}\n{msg}", keyboard=await kbs.configure_chat(**payload),
    )


@bot.on.message(ButtonRule("activate_chat"))
async def activate_chat(ans: Message):
    payload = json.loads(ans.payload)
    payload.pop("button")
    chat = await Chat.get(chat_id=payload["chat_id"])
    chat.active = 1
    await chat.save()
    chat_type = abs(payload["chat_type"] - 1)
    chat = await Chat.get_or_none(chat_type=chat_type, group_id=payload["group_id"])
    if chat:
        chat.active = 0
        await chat.save()
    await ans(
        "Чат выбран для отправки рассылок",
        keyboard=await kbs.configure_chat(
            payload["group_id"], payload["chat_id"], payload["chat_type"], 1
        ),
    )


@bot.on.message(ButtonRule("delete_chat"))
async def delete_chat(ans: Message):
    payload = json.loads(ans.payload)
    chat = await Chat.get_or_none(chat_id=payload["chat_id"])
    if chat:
        await chat.delete()
    await CachedChat.get_or_create(chat_id=payload["chat_id"])
    await ans("Чат удален", keyboard=await kbs.group_settings(ans.from_id))


@bot.on.message(ButtonRule("register_chat"))
async def registrate_chat(ans: Message):
    await ans("Выберите чат для регистрации", keyboard=await kbs.free_chats(bot))


@bot.on.message(ButtonRule("add_chat"))
async def select_type_of_new_chat(ans: Message):
    payload = json.loads(ans.payload)
    await ans(
        f"Укажите тип для чата \"{payload['title']}\"",
        keyboard=await kbs.free_types_of_chats(ans.from_id, payload["chat_id"]),
    )


@bot.on.message(ButtonRule("bind_chat"))
async def bind_chat(ans: Message):
    payload = json.loads(ans.payload)
    chat = await CachedChat.get_or_none(chat_id=payload["chat_id"])
    if chat:
        await chat.delete()
    data = await db.get_ownership_of_admin(ans.from_id)
    await Chat.create(
        chat_id=payload["chat_id"],
        alma_mater_id=data["alma_mater_id"],
        group_id=data["group_id"],
        chat_type=payload["chat_type"],
        active=0,
    )
    await ans("Чат добавлен", keyboard=await kbs.group_settings(ans.from_id))


@bot.on.message(StateRule("main"), ButtonRule("chat_config"))
async def change_active_chat(ans: Message):
    user = await utils.get_storage(ans.from_id)
    chat_id = user.current_chat
    chat = await Chat.get(id=chat_id)
    chat_type = chat.chat_type
    chat_type = 0 if chat_type else 1
    admin = await Administrator.get(vk_id=ans.from_id)
    chat = await Chat.get_or_none(
        alma_mater=admin.alma_mater_id, group=admin.group_id, chat_type=chat_type,
    )
    if chat is not None:
        user.current_chat = chat.id
        await user.save()
        await ans(
            "Параметры изменены",
            keyboard=kbs.admin_settings(user.names_usage, chat.chat_type),
        )
    else:
        chat_text = "Основной" if chat_type else "Тестовый"
        await ans(f"{chat_text} чат не настроен")


@bot.on.message(StateRule("main"), ButtonRule("names_usage"))
async def change_names_usage(ans: Message):
    user = await utils.get_storage(ans.from_id)
    user.names_usage = not user.names_usage
    chat_id = user.current_chat
    chat = await Chat.get(id=chat_id)
    await user.save()
    await ans(
        "Параметры изменены",
        keyboard=kbs.admin_settings(user.names_usage, chat.chat_type),
    )


@bot.on.message(ButtonRule("web"))
async def open_mailings(ans: Message):
    await ans("Здесь будет доступ к вебу...")


loop = asyncio.get_event_loop()
loop.run_until_complete(init_db())
bot.run_polling(skip_updates=False)
