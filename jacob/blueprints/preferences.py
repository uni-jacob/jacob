"""Модуль Настройки."""

import os

import requests
import ujson
from bs4 import BeautifulSoup
from loguru import logger
from vkwave import api
from vkwave import bots
from vkwave import client

from jacob.database import models
from jacob.database import utils as db
from jacob.services import chats
from jacob.services import filters
from jacob.services import keyboard as kbs
from jacob.services.logger import config as logger_config

preferences_router = bots.DefaultRouter()
api_session = api.API(tokens=os.getenv("VK_TOKEN"), clients=client.AIOHTTPClient())
api_context = api_session.get_context()
logger.configure(**logger_config.config)


@bots.simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "settings"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _open_preferences(ans: bots.SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        active_group = db.admin.get_active_group(
            db.students.get_system_id_of_student(ans.object.object.message.from_id),
        )
        await ans.answer(
            "Настройки\nАктивная группа: {0} ({1})".format(
                active_group.group_num,
                active_group.specialty,
            ),
            keyboard=kbs.preferences.preferences(
                db.students.get_system_id_of_student(ans.object.object.message.peer_id),
            ),
        )


@bots.simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "configure_chats"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _list_of_chats(ans: bots.SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        await ans.answer(
            "Список подключенных чатов",
            keyboard=await kbs.preferences.connected_chats(
                db.students.get_system_id_of_student(
                    ans.object.object.message.from_id,
                ),
            ),
        )


@bots.simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "chat"}),  # TODO: Ввести свой статус этому блоку!
    ~filters.StateFilter("confirm_call"),
    ~filters.StateFilter("confirm_debtors_call"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()  # TODO: Refactor!
async def _configure_chat(ans: bots.SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = ujson.loads(ans.object.object.message.payload)
        chat_object = models.Chat.get_by_id(payload["chat_id"])
        query = await api_context.messages.get_conversations_by_id(
            peer_ids=chat_object.chat_id,
            group_id=os.getenv("GROUP_ID"),
        )
        chat_objects = query.response.items
        try:
            chat_title = chat_objects[0].chat_settings.title
        except IndexError:
            chat_title = "???"
        await ans.answer(
            "Настройки чата {0}".format(chat_title),
            keyboard=kbs.preferences.configure_chat(chat_objects.id),
        )


@bots.simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "remove_chat"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _delete_chat(ans: bots.SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = ujson.loads(ans.object.object.message.payload)
        db.chats.delete_chat(payload["chat"])
        chat_objects = db.chats.get_list_of_chats_by_group(
            db.admin.get_active_group(
                db.students.get_system_id_of_student(ans.object.object.message.from_id),
            ),
        )
        try:
            chat_id = chat_objects[0].id
        except IndexError:
            chat_id = None
        db.shortcuts.update_admin_storage(
            db.students.get_system_id_of_student(ans.object.object.message.from_id),
            current_chat_id=chat_id,
        )
        await ans.answer(
            "Чат удален",
            keyboard=await kbs.preferences.connected_chats(
                db.students.get_system_id_of_student(
                    ans.object.object.message.from_id,
                ),
            ),
        )


@bots.simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "reg_chat"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _generate_confirm_message(ans: bots.SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        confirm_message = chats.get_confirm_message()
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


@bots.simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "cancel"}),
    filters.StateFilter("confirm_chat_register"),
)
@logger.catch()
async def _cancel_register_chat(ans: bots.SimpleBotEvent):
    db.shortcuts.clear_admin_storage(
        db.students.get_system_id_of_student(ans.object.object.message.from_id),
    )
    await ans.answer(
        "Регистрация чата отменена",
        keyboard=await kbs.preferences.connected_chats(
            db.students.get_system_id_of_student(
                ans.object.object.message.from_id,
            ),
        ),
    )


@bots.simple_bot_message_handler(
    preferences_router,
    filters.StateFilter("confirm_chat_register"),
    bots.MessageFromConversationTypeFilter("from_chat"),
)
@logger.catch()
async def _register_chat(ans: bots.SimpleBotEvent):  # TODO: Refactor!
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        store = db.admin.get_admin_storage(
            db.students.get_system_id_of_student(ans.object.object.message.from_id),
        )
        message = ans.object.object.message
        admin_vk_id = models.Student.get_by_id(store.id).vk_id
        if store.confirm_message in message.text and message.from_id == admin_vk_id:
            db.shortcuts.clear_admin_storage(
                db.students.get_system_id_of_student(message.from_id),
            )

            group = db.admin.get_active_group(
                db.students.get_system_id_of_student(
                    message.from_id,
                ),
            )
            if db.chats.is_chat_registered(message.peer_id, group):
                await api_context.messages.send(
                    message="Чат уже зарегистрирован в этой группе",
                    peer_id=message.from_id,
                    random_id=0,
                    keyboard=await kbs.preferences.connected_chats(
                        db.students.get_system_id_of_student(
                            message.from_id,
                        ),
                    ),
                )
            else:
                chat = db.chats.register_chat(message.peer_id, group)
                db.shortcuts.update_admin_storage(
                    db.students.get_system_id_of_student(
                        message.from_id,
                    ),
                    current_chat_id=chat.id,
                )
                request = await api_context.messages.get_conversations_by_id(
                    peer_ids=message.peer_id,
                )
                chat_objects = request.response.items
                try:
                    chat_name = chat_objects[0].chat_settings.title
                except IndexError:
                    chat_name = "???"
                await api_context.messages.send(
                    message='Чат "{0}" зарегистрирован'.format(chat_name),
                    peer_id=message.from_id,
                    random_id=0,
                    keyboard=await kbs.preferences.connected_chats(
                        db.students.get_system_id_of_student(
                            message.from_id,
                        ),
                    ),
                )
                await ans.answer("Привет!")


@bots.simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "index_chat"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _index_chat(ans: bots.SimpleBotEvent):  # TODO: Refactor!
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = ujson.loads(ans.object.object.message.payload)
        chat = models.Chat.get_by_id(payload["chat"])

        chat_members = await api_context.messages.get_conversation_members(chat.chat_id)
        group_members = db.students.get_active_students(chat.group_id)

        vk_set = chats.prepare_set_from_vk(chat_members.response.items)
        db_set = chats.prepare_set_from_db(group_members)

        diff_vk_db = vk_set.difference(db_set)  # есть в вк, нет в бд
        diff_db_vk = db_set.difference(vk_set)  # есть в бд, нет в вк

        query = await api_context.users.get(
            user_ids=list(diff_vk_db),
        )
        students = [models.Student.get(vk_id=st) for st in diff_db_vk]

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
                chat.id,
                list(diff_vk_db),
                list(diff_db_vk),
            ),
        )


@bots.simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "register_students"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _register_students(ans: bots.SimpleBotEvent):  # TODO: Refactor!
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = ujson.loads(ans.object.object.message.payload)
        raw_student_data = []
        raw_html = requests.get(payload["students"])
        soup = BeautifulSoup(raw_html.text, "html.parser")
        students_ids = list(map(int, soup.find_all("pre")[1].text.split(",")))
        students = await api_context.users.get(user_ids=students_ids)
        student_last_id = (
            models.Student.select().order_by(models.Student.id.desc()).get().id
        )
        for student in students.response:
            student_last_id += 1
            raw_student_data.append(
                {
                    "id": student_last_id,
                    "first_name": student.first_name,
                    "second_name": student.last_name,
                    "vk_id": student.id,
                    "group_id": payload["group"],
                    "academic_status": 1,
                },
            )
        query = models.Student.insert_many(raw_student_data).execute()

        await ans.answer(
            f"{0} студент(ов) зарегистрировано".format(len(query)),
            keyboard=kbs.preferences.configure_chat(payload["chat_id"]),
        )


@bots.simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "purge_students"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _delete_students(ans: bots.SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = ujson.loads(ans.object.object.message.payload)
        query = 0
        raw_html = requests.get(payload["students"])
        soup = BeautifulSoup(raw_html.text, "html.parser")
        students_ids = list(map(int, soup.find_all("pre")[1].text.split(",")))
        for st in students_ids:
            query += models.Student.delete().where(models.Student.vk_id == st).execute()
        await ans.answer(
            f"{0} студент(ов) удалено".format(query),
            keyboard=kbs.preferences.configure_chat(payload["chat_id"]),
        )


@bots.simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "select_group"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _list_of_administrating_groups(ans: bots.SimpleBotEvent):
    await ans.answer(
        "Выберите активную группу",
        keyboard=kbs.preferences.list_of_groups(
            db.students.get_system_id_of_student(ans.object.object.message.from_id),
        ),
    )


@bots.simple_bot_message_handler(
    preferences_router,
    filters.PLFilter({"button": "group"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _select_active_group(ans: bots.SimpleBotEvent):
    payload = ujson.loads(ans.object.object.message.payload)
    db.shortcuts.update_admin_storage(
        db.students.get_system_id_of_student(ans.object.object.message.from_id),
        active_group=payload["group_id"],
    )
    await _open_preferences(ans)