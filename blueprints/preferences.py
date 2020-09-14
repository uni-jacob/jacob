import os

import hyperjson
import requests
from bs4 import BeautifulSoup
from loguru import logger
from vkwave.api import API
from vkwave.bots import DefaultRouter
from vkwave.bots import SimpleBotEvent
from vkwave.bots import simple_bot_message_handler
from vkwave.client import AIOHTTPClient

from database import utils as db
from database.models import Student
from services import filters
from services import keyboard as kbs
from services.chats import prepare_set_from_db
from services.chats import prepare_set_from_vk
from services.logger.config import config

preferences_router = DefaultRouter()
api_session = API(tokens=os.getenv("VK_TOKEN"), clients=AIOHTTPClient())
api = api_session.get_context()
logger.configure(**config)


@simple_bot_message_handler(
    preferences_router, filters.PLFilter({"button": "settings"})
)
@logger.catch()
async def open_preferences(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        group_id = db.admin.get_admin_feud(
            db.students.get_system_id_of_student(ans.object.object.message.peer_id)
        )
        group = db.groups.find_group(id=group_id)
        await ans.answer(
            f"Настройки группы {group.group_num} ({group.specialty})",
            keyboard=kbs.preferences.preferences(),
        )


@simple_bot_message_handler(
    preferences_router, filters.PLFilter({"button": "configure_chats"})
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


@simple_bot_message_handler(preferences_router, filters.PLFilter({"button": "chat"}))
@logger.catch()
async def configure_chat(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = hyperjson.loads(ans.object.object.message.payload)
        chat = db.chats.find_chat(
            group_id=payload["group"], chat_type=payload["chat_type"]
        )
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
)
@logger.catch()
async def delete_chat(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = hyperjson.loads(ans.object.object.message.payload)
        db.chats.delete_chat(payload["chat"])
        db.chats.get_or_create_cached_chat(payload["chat"])
        await ans.answer(
            "Чат удален",
            keyboard=await kbs.preferences.connected_chats(
                ans.object.object.message.from_id
            ),
        )


@simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "reg_chat"}),
)
@logger.catch()
async def show_available_chats(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        await ans.answer(
            "Выберите чат",
            keyboard=await kbs.preferences.cached_chats(
                ans.object.object.message.from_id
            ),
        )


@simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "select_chat_type"}),
)
async def select_chat_type(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = hyperjson.loads(ans.object.object.message.payload)
        await ans.answer(
            "Выберите тип чата",
            keyboard=kbs.preferences.available_chat_types(
                ans.object.object.message.from_id, payload["chat"]
            ),
        )


@simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "register_chat"}),
)
@logger.catch()
async def register_chat(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = hyperjson.loads(ans.object.object.message.payload)
        db.chats.register_chat(payload["chat"], payload["chat_type"], payload["group"])
        db.chats.delete_cached_chat(payload["chat"])
        await ans.answer(
            "Чат зарегистрирован",
            keyboard=await kbs.preferences.connected_chats(
                ans.object.object.message.from_id
            ),
        )


@simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "index_chat"}),
)
@logger.catch()
async def index_chat(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = hyperjson.loads(ans.object.object.message.payload)
        chat = db.chats.find_chat(id=payload["chat"])

        chat_members = await api.messages.get_conversation_members(chat.chat_id)
        group_members = db.students.get_active_students(chat.group_id)

        vk_ = prepare_set_from_vk(chat_members.response.items)
        db_ = prepare_set_from_db(group_members)

        diff_vk_db = vk_.difference(db_)  # есть в вк, нет в бд
        diff_db_vk = db_.difference(vk_)  # есть в бд, нет в вк

        query = await api.users.get(
            user_ids=list(diff_vk_db),
        )
        students = [db.students.find_student(vk_id=st) for st in diff_db_vk]

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
                chat.group_id.id, list(diff_vk_db), list(diff_db_vk), chat.chat_type.id
            ),
        )


@simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "register_students"}),
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
            keyboard=kbs.preferences.configure_chat(
                db.chats.find_chat(
                    group_id=payload["group"], chat_type=payload["chat_type"]
                ).id
            ),
        )


@simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "purge_students"}),
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
            keyboard=kbs.preferences.configure_chat(
                db.chats.find_chat(
                    group_id=payload["group"], chat_type=payload["chat_type"]
                ).id
            ),
        )
