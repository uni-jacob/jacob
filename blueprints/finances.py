import os
import re

import hyperjson
from loguru import logger
from vkwave.api import API
from vkwave.bots import DefaultRouter
from vkwave.bots import SimpleBotEvent
from vkwave.bots import simple_bot_message_handler
from vkwave.client import AIOHTTPClient

from database import utils as db
from services import filters
from services import keyboard as kbs
from services.logger.config import config

finances_router = DefaultRouter()
api_session = API(tokens=os.getenv("VK_TOKEN"), clients=AIOHTTPClient())
api = api_session.get_context()
logger.configure(**config)


@simple_bot_message_handler(finances_router, filters.PLFilter({"button": "finances"}))
async def finances(ans: SimpleBotEvent):
    await ans.answer(
        "Список финансовых категорий",
        keyboard=kbs.finances.list_of_fin_categories(ans.object.object.message.from_id),
    )


@simple_bot_message_handler(
    finances_router, filters.PLFilter({"button": "fin_category"})
)
async def fin_category_menu(ans: SimpleBotEvent):
    payload = hyperjson.loads(ans.object.object.message.payload)
    db.admin.update_admin_storage(
        db.students.get_system_id_of_student(ans.object.object.message.from_id),
        category_id=payload.get("category"),
    )

    if payload.get("category"):
        category_object = db.finances.find_fin_category(id=payload["category"])
    else:
        store = db.admin.get_admin_storage(
            db.students.get_system_id_of_student(ans.object.object.message.from_id)
        )
        category_object = db.finances.find_fin_category(id=store.category_id)

    category_name = category_object.name

    await ans.answer(
        f'Меню категории "{category_name}"', keyboard=kbs.finances.fin_category(),
    )


@simple_bot_message_handler(finances_router, filters.PLFilter({"button": "add_income"}))
async def add_income(ans: SimpleBotEvent):
    db.admin.update_admin_storage(
        db.students.get_system_id_of_student(ans.object.object.message.from_id),
        state_id=db.bot.get_id_of_state("select_donater"),
    )
    await ans.answer(
        "Выберите студента, сдавшего деньги",
        keyboard=kbs.finances.fin_list_of_letters(ans.object.object.message.from_id),
    )


@simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "half"}) & filters.StateFilter("select_donater"),
)
@logger.catch()
async def select_half(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = hyperjson.loads(ans.object.object.message.payload)
        store = db.admin.get_admin_storage(
            db.students.get_system_id_of_student(ans.object.object.message.from_id)
        )
        category = store.category_id
        await ans.answer(
            "Выберите студента, сдавшего деньги",
            keyboard=kbs.call.list_of_letters(payload["half"], "add_income", category),
        )


@simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "letter"}) & filters.StateFilter("select_donater"),
)
async def select_letter(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = hyperjson.loads(ans.object.object.message.payload)
        letter = payload["value"]
        await ans.answer(
            f"Список студентов на букву {letter}",
            keyboard=kbs.call.list_of_students(
                letter, ans.object.object.message.peer_id, payload.get("letters")
            ),
        )


@simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "student"}) & filters.StateFilter("select_donater"),
)
async def select_student(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        payload = hyperjson.loads(ans.object.object.message.payload)
        db.admin.update_admin_storage(
            db.students.get_system_id_of_student(ans.object.object.message.from_id,),
            selected_students=str(payload["student_id"]),
            state_id=db.bot.get_id_of_state("enter_donate_sum"),
        )
        await ans.answer("Введите сумму дохода", keyboard=kbs.common.empty())


@simple_bot_message_handler(
    finances_router, filters.StateFilter("enter_donate_sum"),
)
async def save_donate(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        text = ans.object.object.message.text
        if re.match("^\d+$", text):
            store = db.admin.get_admin_storage(
                db.students.get_system_id_of_student(ans.object.object.message.from_id)
            )
            db.finances.add_or_edit_donate(
                store.category_id, int(store.selected_students), int(text)
            )
            db.admin.clear_admin_storage(
                db.students.get_system_id_of_student(ans.object.object.message.from_id)
            )
            await ans.answer("Доход сохранен", keyboard=kbs.finances.fin_category())
        else:
            await ans.answer("Введите только число")
