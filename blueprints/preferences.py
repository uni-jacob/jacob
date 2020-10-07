import os

import hyperjson
import requests
from bs4 import BeautifulSoup
from loguru import logger
from vkwave.api import API
from vkwave.bots import DefaultRouter
from vkwave.bots import MessageFromConversationTypeFilter
from vkwave.bots import SimpleBotEvent
from vkwave.bots import simple_bot_message_handler
from vkwave.client import AIOHTTPClient

from database import utils as db
from database.models import Chat
from database.models import Group
from database.models import Student
from services import filters
from services import keyboard as kbs
from services.chats import get_confirm_message
from services.chats import prepare_set_from_db
from services.chats import prepare_set_from_vk
from services.logger.config import config

preferences_router = DefaultRouter()
api_session = API(tokens=os.getenv("VK_TOKEN"), clients=AIOHTTPClient())
api = api_session.get_context()
logger.configure(**config)


@simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "settings"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def open_preferences(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        # TODO: Изменить механизм получения идшника активной группы
        group_id = db.admin.get_admin_feud(
            db.students.get_system_id_of_student(ans.object.object.message.peer_id)
        )
        group = Group.get_by_id(group_id)
        await ans.answer(
            f"Настройки\nАктивная группа: {group.group_num} ({group.specialty})",
            keyboard=kbs.preferences.preferences(
                db.students.get_system_id_of_student(ans.object.object.message.peer_id)
            ),
        )


@simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "configure_chats"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def list_of_chats(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        await ans.answer(
            "Список подключенных чатов",
            keyboard=await kbs.preferences.connected_chats(
                ans.object.object.message.peer_id
            ),
        )


@simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "chat"}),
    ~filters.StateFilter("confirm_call"),
    ~filters.StateFilter("confirm_debtors_call"),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def configure_chat(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = hyperjson.loads(ans.object.object.message.payload)
        chat = Chat.get_by_id(payload["chat_id"])
        chat_object = await api.messages.get_conversations_by_id(
            peer_ids=chat.chat_id, group_id=os.getenv("GROUP_ID")
        )
        try:
            chat_title = chat_object.response.items[0].chat_settings.title
        except IndexError:
            chat_title = "???"
        await ans.answer(
            f"Настройки чата {chat_title}",
            keyboard=kbs.preferences.configure_chat(chat.id),
        )


@simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "remove_chat"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def delete_chat(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = hyperjson.loads(ans.object.object.message.payload)
        db.chats.delete_chat(payload["chat"])
        chats = db.chats.get_list_of_chats_by_group(ans.object.object.message.from_id)
        try:
            chat_id = chats[0].id
        except IndexError:
            chat_id = None
        db.shortcuts.update_admin_storage(
            db.students.get_system_id_of_student(ans.object.object.message.from_id),
            current_chat_id=chat_id,
        )
        await ans.answer(
            "Чат удален",
            keyboard=await kbs.preferences.connected_chats(
                ans.object.object.message.from_id
            ),
        )


@simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "reg_chat"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def generate_confirm_message(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        confirm_message = get_confirm_message()
        db.shortcuts.update_admin_storage(
            db.students.get_system_id_of_student(ans.object.object.message.from_id),
            state_id=db.bot.get_id_of_state("confirm_chat_register"),
            confirm_message=confirm_message,
        )
        await ans.answer(
            "Отправьте сообщение с кодовой фразой в чат, который нужно зарегистрировать",
            keyboard=kbs.common.cancel(),
        )

        await ans.answer(confirm_message)


@simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "cancel"}),
    filters.StateFilter("confirm_chat_register"),
)
@logger.catch()
async def cancel_register_chat(ans: SimpleBotEvent):
    db.shortcuts.clear_admin_storage(
        db.students.get_system_id_of_student(ans.object.object.message.from_id)
    )
    await ans.answer(
        "Регистрация чата отменена",
        keyboard=await kbs.preferences.connected_chats(
            ans.object.object.message.from_id
        ),
    )


@simple_bot_message_handler(
    preferences_router,
    filters.StateFilter("confirm_chat_register"),
    MessageFromConversationTypeFilter("from_chat"),
)
@logger.catch()
async def register_chat(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        store = db.admin.get_admin_storage(
            db.students.get_system_id_of_student(ans.object.object.message.from_id)
        )
        if (
            store.confirm_message in ans.object.object.message.text
            and ans.object.object.message.from_id == Student.get_by_id(store.id).vk_id
        ):
            db.shortcuts.clear_admin_storage(
                db.students.get_system_id_of_student(ans.object.object.message.from_id)
            )

            group = Student.get(vk_id=ans.object.object.message.from_id).group_id.id
            chat = db.chats.register_chat(ans.object.object.message.peer_id, group)
            db.shortcuts.update_admin_storage(
                db.students.get_system_id_of_student(ans.object.object.message.from_id),
                current_chat_id=chat.id,
            )
            try:
                chat_object = await api.messages.get_conversations_by_id(
                    peer_ids=ans.object.object.message.peer_id
                )
                chat_name = chat_object.response.items[0].chat_settings.title
            except IndexError:
                chat_name = "???"
            await api.messages.send(
                message=f'Чат "{chat_name}" зарегистрирован',
                peer_id=ans.object.object.message.from_id,
                random_id=0,
                keyboard=await kbs.preferences.connected_chats(
                    ans.object.object.message.from_id
                ),
            )
            await ans.answer("Привет!")


@simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "index_chat"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def index_chat(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = hyperjson.loads(ans.object.object.message.payload)
        chat = Chat.get_by_id(payload["chat"])

        chat_members = await api.messages.get_conversation_members(chat.chat_id)
        group_members = db.students.get_active_students(chat.group_id)

        vk_ = prepare_set_from_vk(chat_members.response.items)
        db_ = prepare_set_from_db(group_members)

        diff_vk_db = vk_.difference(db_)  # есть в вк, нет в бд
        diff_db_vk = db_.difference(vk_)  # есть в бд, нет в вк

        query = await api.users.get(
            user_ids=list(diff_vk_db),
        )
        students = [Student.get(vk_id=st) for st in diff_db_vk]

        vk_list = [
            f"- @id{st.id} ({st.first_name} {st.last_name})" for st in query.response
        ]
        db_list = [
            f"- @id{st.vk_id} ({st.first_name} {st.second_name})" for st in students
        ]

        sep = "\n"

        await ans.answer(
            f"""
        Добавлены в чат, но не зарегистрированы в системе:\n{sep.join(vk_list) or "⸻"}
    Зарегистрированы в системе, но не добавлены в чат:\n{sep.join(db_list) or "⸻"}
    Вы можете зарегистрировать студентов в системе в автоматическом режиме,
     нажав соответствующую кнопку на клавиатуре. Студенты появятся в базе данных,
     вам останется лишь изменить тип их обучения (бюджет/контракт и пр.)
        """,
            keyboard=kbs.preferences.index_chat(
                chat.id, list(diff_vk_db), list(diff_db_vk)
            ),
        )


@simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "register_students"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def register_students(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = hyperjson.loads(ans.object.object.message.payload)
        data = []
        raw_html = requests.get(payload["students"])
        soup = BeautifulSoup(raw_html.text, "html.parser")
        students_ids = list(map(int, soup.find_all("pre")[1].text.split(",")))
        students = await api.users.get(user_ids=students_ids)
        student_last_id = Student.select().order_by(Student.id.desc()).get().id
        for student in students.response:
            student_last_id += 1
            data.append(
                {
                    "id": student_last_id,
                    "first_name": student.first_name,
                    "second_name": student.last_name,
                    "vk_id": student.id,
                    "group_id": payload["group"],
                    "academic_status": 1,
                }
            )
        query = Student.insert_many(data).execute()

        await ans.answer(
            f"{len(query)} студент(ов) зарегистрировано",
            keyboard=kbs.preferences.configure_chat(payload["chat_id"]),
        )


@simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "purge_students"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def delete_students(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = hyperjson.loads(ans.object.object.message.payload)
        query = 0
        raw_html = requests.get(payload["students"])
        soup = BeautifulSoup(raw_html.text, "html.parser")
        students_ids = list(map(int, soup.find_all("pre")[1].text.split(",")))
        for st in students_ids:
            query += Student.delete().where(Student.vk_id == st).execute()
        await ans.answer(
            f"{query} студент(ов) удалено",
            keyboard=kbs.preferences.configure_chat(payload["chat_id"]),
        )


@simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "select_group"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def list_of_administrating_groups(ans: SimpleBotEvent):
    await ans.answer(
        "Выберите активную группу",
        keyboard=kbs.preferences.list_of_groups(
            db.students.get_system_id_of_student(ans.object.object.message.from_id)
        ),
    )


@simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "group"}),
    MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def select_active_group(ans: SimpleBotEvent):
    payload = hyperjson.loads(ans.object.object.message.payload)
    db.shortcuts.update_admin_storage(
        db.students.get_system_id_of_student(ans.object.object.message.from_id),
        active_group=payload["group_id"],
    )
    await open_preferences(ans)
