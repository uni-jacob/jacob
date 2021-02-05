"""Блок Финансы."""

import os
import re

import ujson
from loguru import logger
from vkwave import api, bots, client

from jacob.database import models
from jacob.database import utils as db
from jacob.services import decorators, filters
from jacob.services import keyboard as kbs
from jacob.services.finances import generate_debtors_call
from jacob.services.logger.config import config

finances_router = bots.DefaultRouter()
api_session = api.API(tokens=os.getenv("VK_TOKEN"), clients=client.AIOHTTPClient())
api_context = api_session.get_context()
logger.configure(**config)


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "finances"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
@decorators.context_logger
async def _finances(ans: bots.SimpleBotEvent):
    await ans.answer(
        "Список финансовых категорий",
        keyboard=kbs.finances.list_of_fin_categories(
            db.students.get_system_id_of_student(ans.object.object.message.from_id),
        ),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "create_finances_category"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
@decorators.context_logger
async def _create_category(ans: bots.SimpleBotEvent):
    db.shortcuts.update_admin_storage(
        db.students.get_system_id_of_student(ans.object.object.message.from_id),
        state_id=db.bot.get_id_of_state("wait_for_finances_category_description"),
    )
    await ans.answer(
        "Отправьте название категории и сумму сбора, разделенные пробелом",
        keyboard=kbs.common.cancel(),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "cancel"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
@decorators.context_logger
async def _cancel_creating_category(ans: bots.SimpleBotEvent):
    db.shortcuts.update_admin_storage(
        db.students.get_system_id_of_student(ans.object.object.message.from_id),
        state_id=db.bot.get_id_of_state("main"),
    )
    await ans.answer(
        "Создание категории отменено",
        keyboard=kbs.finances.list_of_fin_categories(
            db.students.get_system_id_of_student(ans.object.object.message.from_id),
        ),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_wait_category_desc"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
@decorators.context_logger
async def _register_category(ans: bots.SimpleBotEvent):
    if re.match(r"^\w+ \d+$", ans.object.object.message.text):
        message = ans.object.object.message
        category = db.finances.create_finances_category(
            db.admin.get_active_group(
                db.students.get_system_id_of_student(message.from_id),
            ),
            *message.text.split(),
        )
        db.shortcuts.update_admin_storage(
            db.students.get_system_id_of_student(message.from_id),
            state_id=db.bot.get_id_of_state("main"),
        )
        await ans.answer(
            "Категория {0} зарегистрирована".format(category.name),
            keyboard=kbs.finances.list_of_fin_categories(
                db.students.get_system_id_of_student(message.from_id),
            ),
        )
    else:
        await ans.answer("Неверный формат данных")


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "fin_category"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
@decorators.context_logger
async def _fin_category_menu(ans: bots.SimpleBotEvent):
    payload = ujson.loads(ans.object.object.message.payload)
    db.shortcuts.update_admin_storage(
        db.students.get_system_id_of_student(ans.object.object.message.from_id),
        category_id=payload.get("category"),
    )

    if payload.get("category"):
        category_object = models.FinancialCategory.get_by_id(payload["category"])
    else:
        store = db.admin.get_admin_storage(
            db.students.get_system_id_of_student(ans.object.object.message.from_id),
        )
        category_object = models.FinancialCategory.get_by_id(store.category_id)

    category_name = category_object.name

    await ans.answer(
        'Меню категории "{0}"'.format(category_name),
        keyboard=kbs.finances.fin_category(),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "add_income"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
@decorators.context_logger
async def _add_income(ans: bots.SimpleBotEvent):
    db.shortcuts.update_admin_storage(
        db.students.get_system_id_of_student(ans.object.object.message.from_id),
        state_id=db.bot.get_id_of_state("select_donater"),
    )
    await ans.answer(
        "Выберите студента, сдавшего деньги",
        keyboard=kbs.finances.IncomeNavigator(
            db.students.get_system_id_of_student(ans.object.object.message.from_id),
        )
        .render()
        .menu(),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "half"}) & filters.StateFilter("fin_select_donater"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
@decorators.context_logger
async def _select_half(ans: bots.SimpleBotEvent):
    payload = ujson.loads(ans.object.object.message.payload)
    await ans.answer(
        "Выберите студента, сдавшего деньги",
        keyboard=kbs.finances.IncomeNavigator(
            db.students.get_system_id_of_student(ans.object.object.message.from_id),
        )
        .render()
        .submenu(payload["half"]),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "letter"}) & filters.StateFilter("fin_select_donater"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch
@decorators.context_logger
async def _select_letter(ans: bots.SimpleBotEvent):
    payload = ujson.loads(ans.object.object.message.payload)
    letter = payload["value"]
    await ans.answer(
        "Список студентов на букву {0}".format(letter),
        keyboard=kbs.finances.IncomeNavigator(
            db.students.get_system_id_of_student(ans.object.object.message.peer_id),
        )
        .render()
        .students(letter),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "student"}) & filters.StateFilter("fin_select_donater"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch
@decorators.context_logger
async def _select_student(ans: bots.SimpleBotEvent):
    payload = ujson.loads(ans.object.object.message.payload)
    db.shortcuts.update_admin_storage(
        db.students.get_system_id_of_student(
            ans.object.object.message.from_id,
        ),
        selected_students=str(payload["student_id"]),
        state_id=db.bot.get_id_of_state("enter_donate_sum"),
    )
    await ans.answer("Введите сумму дохода", keyboard=kbs.common.empty())


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_enter_donate_sum"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
@decorators.context_logger
async def _save_donate(ans: bots.SimpleBotEvent):
    text = ans.object.object.message.text
    if re.match(r"^\d+$", text):
        store = db.admin.get_admin_storage(
            db.students.get_system_id_of_student(ans.object.object.message.from_id),
        )
        db.finances.add_or_edit_donate(
            store.category_id,
            int(store.selected_students),
            int(text),
        )
        db.shortcuts.clear_admin_storage(
            db.students.get_system_id_of_student(ans.object.object.message.from_id),
        )
        await ans.answer("Доход сохранен", keyboard=kbs.finances.fin_category())
    else:
        await ans.answer("Введите только число")


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "show_debtors"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
@decorators.context_logger
async def _call_debtors(ans: bots.SimpleBotEvent):
    admin_id = db.students.get_system_id_of_student(ans.object.object.message.from_id)
    group_id = db.admin.get_active_group(admin_id)
    if db.chats.get_list_of_chats_by_group(group_id):
        msgs = generate_debtors_call(admin_id)
        db.shortcuts.update_admin_storage(
            admin_id,
            state_id=db.bot.get_id_of_state("confirm_debtors_call"),
        )
        store = db.admin.get_admin_storage(admin_id)
        chat_id = models.Chat.get_by_id(store.current_chat_id).chat_id
        chat_object = await api_context.messages.get_conversations_by_id(chat_id)
        chats = chat_object.response.items
        try:
            chat_title = chats[0].chat_settings.title
        except IndexError:
            chat_title = "???"
        for msg in msgs:
            await ans.answer(msg)
        if len(msgs) > 1:
            text = "Сообщения будут отправлены в {0}"
        else:
            text = "Сообщение будет отправлено в {0}"
        await ans.answer(
            text.format(chat_title),
            keyboard=kbs.finances.confirm_debtors_call(),
        )
    else:
        await ans.answer(
            "У вашей группы нет зарегистрированных чатов. Возврат в главное меню",
            keyboard=kbs.finances.fin_category(),
        )


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_confirm_debtors_call"),
    filters.PLFilter({"button": "chat_config"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
@decorators.context_logger
async def _select_chat_debtors(ans: bots.SimpleBotEvent):
    kb = await kbs.common.list_of_chats(
        db.students.get_system_id_of_student(ans.object.object.message.from_id),
    )
    await ans.answer("Выберите чат", keyboard=kb.get_keyboard())


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_confirm_debtors_call"),
    filters.PLFilter({"button": "chat"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
@decorators.context_logger
async def _save_chat_debtors(ans: bots.SimpleBotEvent):
    payload = ujson.loads(ans.object.object.message.payload)
    db.shortcuts.update_admin_storage(
        db.students.get_system_id_of_student(ans.object.object.message.from_id),
        current_chat_id=payload["chat_id"],
    )
    await _call_debtors(ans)


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_confirm_debtors_call"),
    filters.PLFilter({"button": "confirm"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
@decorators.context_logger
async def _confirm_call_debtors(ans: bots.SimpleBotEvent):
    msgs = generate_debtors_call(
        db.students.get_system_id_of_student(ans.object.object.message.from_id),
    )
    chat = db.shortcuts.get_active_chat(
        db.students.get_system_id_of_student(ans.object.object.message.from_id),
    ).chat_id
    db.shortcuts.update_admin_storage(
        db.students.get_system_id_of_student(ans.object.object.message.from_id),
        state_id=db.bot.get_id_of_state("main"),
    )
    for msg in msgs:
        await api_context.messages.send(peer_id=chat, message=msg, random_id=0)
    await ans.answer("Призыв отправлен", keyboard=kbs.finances.fin_category())


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_confirm_debtors_call"),
    filters.PLFilter({"button": "deny"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
@decorators.context_logger
async def _deny_call_debtors(ans: bots.SimpleBotEvent):
    db.shortcuts.update_admin_storage(
        db.students.get_system_id_of_student(ans.object.object.message.from_id),
        state_id=db.bot.get_id_of_state("main"),
    )
    await ans.answer("Отправка отменена", keyboard=kbs.finances.fin_category())


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "add_expense"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _add_expense(ans: bots.SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        db.shortcuts.update_admin_storage(
            db.students.get_system_id_of_student(ans.object.object.message.from_id),
            state_id=db.bot.get_id_of_state("enter_expense_summ"),
        )
        await ans.answer("Введите сумму расхода")


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_enter_expense_summ"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _save_expense(ans: bots.SimpleBotEvent):
    with logger.contextualize(user_id=ans.object.object.message.from_id):
        text = ans.object.object.message.text
        if re.match(r"^\d+$", text):
            store = db.admin.get_admin_storage(
                db.students.get_system_id_of_student(ans.object.object.message.from_id),
            )
            db.finances.add_expense(store.category_id, int(text))
            db.shortcuts.clear_admin_storage(
                db.students.get_system_id_of_student(ans.object.object.message.from_id),
            )
            await ans.answer("Расход сохранен", keyboard=kbs.finances.fin_category())
        else:
            await ans.answer("Введите только число")


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "show_stats"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
@logger.catch()
async def _get_statistics(ans: bots.SimpleBotEvent):
    store = db.admin.get_admin_storage(
        db.students.get_system_id_of_student(ans.object.object.message.from_id),
    )
    donates_summ = db.finances.calculate_donates_in_category(store.category_id)
    expenses_summ = db.finances.calculate_expenses_in_category(store.category_id)
    await ans.answer(
        "Статистика\nСобрано: {0} руб.\nПотрачено: {1} руб.".format(
            donates_summ,
            expenses_summ,
        ),
    )
