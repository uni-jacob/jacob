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
from services.finances import generate_debtors_call
from services.logger.config import config

finances_router = DefaultRouter()
api_session = API(tokens=os.getenv("VK_TOKEN"), clients=AIOHTTPClient())
api = api_session.get_context()
logger.configure(**config)


@simple_bot_message_handler(finances_router, filters.PLFilter({"button": "finances"}))
@logger.catch()
async def finances(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        await ans.answer(
            "Список финансовых категорий",
            keyboard=kbs.finances.list_of_fin_categories(
                ans.object.object.message.from_id
            ),
        )


@simple_bot_message_handler(
    finances_router, filters.PLFilter({"button": "fin_category"})
)
@logger.catch()
async def fin_category_menu(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
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
            f'Меню категории "{category_name}"',
            keyboard=kbs.finances.fin_category(),
        )


@simple_bot_message_handler(finances_router, filters.PLFilter({"button": "add_income"}))
@logger.catch()
async def add_income(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        db.admin.update_admin_storage(
            db.students.get_system_id_of_student(ans.object.object.message.from_id),
            state_id=db.bot.get_id_of_state("select_donater"),
        )
        await ans.answer(
            "Выберите студента, сдавшего деньги",
            keyboard=kbs.finances.fin_list_of_letters(
                ans.object.object.message.from_id
            ),
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
            db.students.get_system_id_of_student(
                ans.object.object.message.from_id,
            ),
            selected_students=str(payload["student_id"]),
            state_id=db.bot.get_id_of_state("enter_donate_sum"),
        )
        await ans.answer("Введите сумму дохода", keyboard=kbs.common.empty())


@simple_bot_message_handler(
    finances_router,
    filters.StateFilter("enter_donate_sum"),
)
@logger.catch()
async def save_donate(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        text = ans.object.object.message.text
        if re.match(r"^\d+$", text):
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


@simple_bot_message_handler(
    finances_router, filters.PLFilter({"button": "show_debtors"})
)
@logger.catch()
async def call_debtors(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        msgs = generate_debtors_call(
            db.students.get_system_id_of_student(ans.object.object.message.from_id)
        )
        db.admin.update_admin_storage(
            db.students.get_system_id_of_student(ans.object.object.message.from_id),
            state_id=db.bot.get_id_of_state("confirm_debtors_call"),
        )
        for msg in msgs:
            await ans.answer(msg)
        if len(msgs) > 1:
            text = ("Сообщения будут отправлены в ваш активный чат",)
        else:
            text = ("Сообщение будет отправлено в ваш активный чат",)
        await ans.answer(
            text,
            keyboard=kbs.common.prompt().get_keyboard(),
        )


@simple_bot_message_handler(
    finances_router,
    filters.StateFilter("confirm_debtors_call"),
    filters.PLFilter({"button": "confirm"}),
)
@logger.catch()
async def confirm_call_debtors(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        msgs = generate_debtors_call(
            db.students.get_system_id_of_student(ans.object.object.message.from_id)
        )
        chat = db.shortcuts.get_active_chat(
            db.students.get_system_id_of_student(ans.object.object.message.from_id)
        ).chat_id
        db.admin.update_admin_storage(
            db.students.get_system_id_of_student(ans.object.object.message.from_id),
            state_id=db.bot.get_id_of_state("main"),
        )
        for msg in msgs:
            await api.messages.send(peer_id=chat, message=msg, random_id=0)
        await ans.answer("Призыв отправлен", keyboard=kbs.finances.fin_category())


@simple_bot_message_handler(
    finances_router,
    filters.StateFilter("confirm_debtors_call"),
    filters.PLFilter({"button": "deny"}),
)
@logger.catch()
async def deny_call_debtors(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        db.admin.update_admin_storage(
            db.students.get_system_id_of_student(ans.object.object.message.from_id),
            state_id=db.bot.get_id_of_state("main"),
        )
        await ans.answer("Отправка отменена", keyboard=kbs.finances.fin_category())


@simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "add_expense"}),
)
@logger.catch()
async def add_expense(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        db.admin.update_admin_storage(
            db.students.get_system_id_of_student(ans.object.object.message.from_id),
            state_id=db.bot.get_id_of_state("enter_expense_summ"),
        )
        await ans.answer("Введите сумму расхода")


@simple_bot_message_handler(
    finances_router,
    filters.StateFilter("enter_expense_summ"),
)
@logger.catch()
async def save_expense(ans: SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        text = ans.object.object.message.text
        if re.match(r"^\d+$", text):
            store = db.admin.get_admin_storage(
                db.students.get_system_id_of_student(ans.object.object.message.from_id)
            )
            db.finances.add_expense(store.category_id, int(text))
            db.admin.clear_admin_storage(
                db.students.get_system_id_of_student(ans.object.object.message.from_id)
            )
            await ans.answer("Расход сохранен", keyboard=kbs.finances.fin_category())
        else:
            await ans.answer("Введите только число")


@simple_bot_message_handler(finances_router, filters.PLFilter({"button": "show_stats"}))
@logger.catch()
async def get_statistics(ans: SimpleBotEvent):
    await ans.answer("Статистика")
