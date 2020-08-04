import json
import os
import random

from vkbottle import Bot
from vkbottle import Message
from vkbottle.rule import AttachmentRule
from vkbottle.rule import CommandRule
from vkbottle.rule import VBMLRule
from vkbottle.rule import filters

from database import Database
from database import utils
from keyboard import Keyboards
from utils import call
from utils import media
from utils.filters import NotFilter
from utils.rules import ButtonRule
from utils.rules import StateRule

bot = Bot(os.environ["VK_TOKEN"])
db = Database(os.environ["DATABASE_URL"])
kbs = Keyboards()


@bot.on.message(text="начать", lower=True)
async def start_bot(ans: Message):
    await ans(f"Привет!", keyboard=await kbs.main_menu(ans.from_id))


@bot.on.message(ButtonRule("home"))
async def start_bot(ans: Message):
    await ans(f"Главное меню", keyboard=await kbs.main_menu(ans.from_id))


@bot.on.chat_invite()
async def invite_to_chat(ans: Message):
    await utils.save_chat_to_cache(ans.peer_id)
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

    if not ans.reply_message and not ans.fwd_messages:
        await ans("Эта команда работает только в ответ на какое-то сообщение")


@bot.on.message(ButtonRule("call"))
async def open_call(ans: Message):
    state = await utils.get_id_of_state("wait_call_text")
    await utils.update_storage(ans.from_id, state_id=state)
    store = await utils.get_storage(ans.from_id)
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
    if ans.attachments:
        attaches = await media.load_attachments(bot, ans.attachments, ans.from_id)
        await utils.update_storage(ans.from_id, attaches=attaches)
    await utils.update_storage(
        ans.from_id, state_id=await utils.get_id_of_state(), text=ans.text
    )
    await ans(
        message="Выберите призываемых:", keyboard=await kbs.call_interface(ans.from_id)
    )


@bot.on.message(ButtonRule("skip_call_message"))
async def generate_call_kb(ans: Message):
    await utils.update_storage(ans.from_id, state_id=await utils.get_id_of_state())
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
    store = await utils.get_storage(ans.from_id)
    st = store["selected_students"] or ""
    students = [i for i in st.split(",") if i]
    if str(payload["student_id"]) not in students:
        students.append(str(payload["student_id"]))
        await utils.update_storage(ans.from_id, selected_students=",".join(students))
        await ans(f"{payload['name']} добавлен к списку призывемых")
    else:
        students.remove(str(payload["student_id"]))
        await utils.update_storage(ans.from_id, selected_students=",".join(students))
        await ans(f"{payload['name']} убран из списка призывемых")


@bot.on.message(ButtonRule("save_selected"))
async def save_call(ans: Message):
    store = await utils.get_storage(ans.from_id)
    await utils.update_storage(
        ans.from_id, state_id=await utils.get_id_of_state("confirm_call")
    )
    chat_text = "основную" if store["current_chat"] else "тестовую"
    message = await call.generate_message(ans.from_id)
    attachments = store["attaches"]
    await ans(f"Это сообщение будет отправлено в {chat_text} беседу:")
    await ans(
        message=message,
        attachment=attachments,
        keyboard=kbs.call_prompt(store["names_usage"], store["current_chat"]),
    )


@bot.on.message(ButtonRule("call_all"))
async def call_all_of_them(ans: Message):
    students = await db.get_active_students(ans.from_id)
    called = []
    for student in students:
        called.append(str(student["id"]))
    await utils.update_storage(ans.from_id, selected_students=",".join(called))
    await save_call(ans)


@bot.on.message(StateRule("confirm_call"), ButtonRule("confirm"))
async def confirm_call(ans: Message):
    store = await utils.get_storage(ans.from_id)
    student = await utils.find_student(fetch="one", st_id=store["id"])
    await utils.update_storage(ans.from_id, state_id=await utils.get_id_of_state())
    message = await call.generate_message(ans.from_id)
    attachments = store["attaches"]
    chat = await utils.find_chat(
        fetch="one", group_id=student["group_id"], chat_type=store["current_chat"]
    )
    await bot.api.messages.send(
        random_id=random.getrandbits(64),
        peer_id=chat["chat_id"],
        message=message,
        attachment=attachments,
    )
    await utils.clear_storage(ans.from_id)
    await ans("Сообщение отправлено", keyboard=await kbs.main_menu(ans.from_id))


@bot.on.message(StateRule("confirm_call"), ButtonRule("deny"))
async def deny_call(ans: Message):
    await utils.clear_storage(ans.from_id)
    await utils.update_storage(ans.from_id, state_id=await utils.get_id_of_state())
    await ans("Выполнение команды отменено", keyboard=await kbs.main_menu(ans.from_id))


@bot.on.message(StateRule("confirm_call"), ButtonRule("names_usage"))
async def edit_names_usage(ans: Message):
    store = await utils.get_storage(ans.from_id)
    await utils.update_storage(ans.from_id, names_usage=not store["names_usage"])
    await save_call(ans)


@bot.on.message(StateRule("confirm_call"), ButtonRule("chat_config"))
async def edit_chat(ans: Message):
    store = await utils.get_storage(ans.from_id)
    student = await utils.find_student(fetch="one", st_id=store["id"])
    chat_type = abs(store["current_chat"] - 1)
    chat = await utils.find_chat(
        fetch="one", chat_type=chat_type, group_id=student["group_id"]
    )
    if chat is not None:
        await utils.update_storage(ans.from_id, current_chat=chat_type)
        await save_call(ans)
    else:
        await ans(f"{'Основной' if chat_type else 'Тестовый'} чат не настроен")


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
    store = await utils.get_storage(ans.from_id)
    await ans(
        "Настройки администратора",
        keyboard=kbs.admin_settings(store["names_usage"], store["current_chat"]),
    )


@bot.on.message(ButtonRule("group_settings"))
async def open_group_settings(ans: Message):
    await ans("Настроенные чаты", keyboard=await kbs.group_settings(ans.from_id))


@bot.on.message(ButtonRule("configure_chat"))
async def configure_chat(ans: Message):
    payload = json.loads(ans.payload)
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
    active_chat = await utils.update_chat_activity(1, chat_id=payload["chat_id"])
    chat = await utils.find_chat(
        fetch="one",
        chat_id=payload["chat_id"],  # TODO
        chat_type=abs(active_chat["chat_type"] - 1),
    )
    if chat is not None:
        await utils.update_chat_activity(
            0, chat_id=payload["chat_id"], group_id=payload["group_id"]
        )
    await ans(
        "Чат выбран для отправки рассылок",
        keyboard=await kbs.configure_chat(
            payload["group_id"], payload["chat_id"], payload["chat_type"], 1
        ),
    )


@bot.on.message(ButtonRule("delete_chat"))
async def delete_chat(ans: Message):
    payload = json.loads(ans.payload)
    await utils.unbind_chat(chat_id=payload["chat_id"])
    await utils.save_chat_to_cache(payload["chat_id"])
    await ans(
        "Чат отвязан от вашей группы", keyboard=await kbs.group_settings(ans.from_id)
    )


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
    group_id = await db.get_ownership_of_admin(ans.from_id)
    await utils.delete_chat_from_cache(payload["chat_id"])
    await utils.bind_chat(
        chat_id=payload["payload_id"],
        group_id=group_id,
        chat_type=payload["chat_type"],
        is_active=False,
    )
    await ans("Чат добавлен", keyboard=await kbs.group_settings(ans.from_id))


@bot.on.message(StateRule("main"), ButtonRule("chat_config"))
async def change_active_chat(ans: Message):
    store = await utils.get_storage(ans.from_id)
    student = await utils.find_student(fetch="one", st_id=store["id"])
    chat_type = abs(store["current_chat"] - 1)
    chat = await utils.find_chat(
        fetch="one", group_id=student["group_id"], chat_type=chat_type
    )
    if chat is not None:
        await utils.update_storage(ans.from_id, current_chat=chat_type)
        await ans(
            "Параметры изменены",
            keyboard=kbs.admin_settings(store["names_usage"], chat_type),
        )
    else:
        await ans(f"{'Основной' if chat_type else 'Тестовый'} чат не настроен")


@bot.on.message(StateRule("main"), ButtonRule("names_usage"))
async def change_names_usage(ans: Message):
    store = await utils.get_storage(ans.from_id)
    await utils.update_storage(ans.from_id, names_usage=not store["names_usage"])
    await ans(
        "Параметры изменены",
        keyboard=kbs.admin_settings(not store["names_usage"], store["current_chat"]),
    )


@bot.on.message(ButtonRule("web"))
async def open_mailings(ans: Message):
    await ans("Здесь будет доступ к вебу...")


bot.run_polling(skip_updates=False)
