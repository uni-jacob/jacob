"""Блок Финансы."""

import os
import re

import aioredis
import ujson
from loguru import logger
from pony import orm
from vkwave import api, bots, client

from jacob.database.utils import chats as chats_utils
from jacob.database.utils import students, finances, admin
from jacob.database.utils.storages import managers
from jacob.services import filters
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
async def _finances(ans: bots.SimpleBotEvent):
    await ans.answer(
        "Список финансовых категорий",
        keyboard=kbs.finances.list_of_fin_categories(
            students.get_system_id_of_student(ans.object.object.message.from_id),
        ),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "create_finances_category"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _create_category(ans: bots.SimpleBotEvent):
    state_storage = managers.StateStorageManager(
        students.get_system_id_of_student(ans.object.object.message.from_id)
    )
    state_storage.update(state=state_storage.get_id_of_state("fin_wait_category_desc"))
    await ans.answer(
        "Отправьте название категории и сумму сбора, разделенные пробелом",
        keyboard=kbs.common.cancel(),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "cancel"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _cancel_creating_category(ans: bots.SimpleBotEvent):
    student_id = students.get_system_id_of_student(ans.object.object.message.from_id)
    state_storage = managers.StateStorageManager(student_id)
    state_storage.update(state=state_storage.get_id_of_state("main"))
    await ans.answer(
        "Создание категории отменено",
        keyboard=kbs.finances.list_of_fin_categories(
            student_id,
        ),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_wait_category_desc"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _register_category(ans: bots.SimpleBotEvent):
    if re.match(r"^\w+ \d+$", ans.object.object.message.text):
        message = ans.object.object.message
        student_id = students.get_system_id_of_student(message.from_id)
        category = finances.get_or_create_finances_category(
            admin.get_active_group(student_id).id,
            *message.text.split(),
        )
        state_storage = managers.StateStorageManager(student_id)
        state_storage.update(state=state_storage.get_id_of_state("main"))
        await ans.answer(
            "Категория {0} зарегистрирована".format(category.name),
            keyboard=kbs.finances.list_of_fin_categories(
                student_id,
            ),
        )
    else:
        await ans.answer("Неверный формат данных")


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "fin_category"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _fin_category_menu(ans: bots.SimpleBotEvent):
    payload = ujson.loads(ans.object.object.message.payload)
    fin_storage = managers.FinancialConfigManager(
        students.get_system_id_of_student(ans.object.object.message.from_id)
    )
    fin_storage.update(financial_category=payload.get("category"))

    with orm.db_session:
        category_name = fin_storage.get_or_create().financial_category.name

    await ans.answer(
        'Меню категории "{0}"'.format(category_name),
        keyboard=kbs.finances.fin_category(),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "add_income"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _add_income(ans: bots.SimpleBotEvent):
    student_id = students.get_system_id_of_student(ans.object.object.message.from_id)
    state_storage = managers.StateStorageManager(student_id)
    state_storage.update(state=state_storage.get_id_of_state("fin_select_donater"))
    await ans.answer(
        "Выберите студента, сдавшего деньги",
        keyboard=kbs.finances.IncomeNavigator(
            students.get_system_id_of_student(ans.object.object.message.from_id),
        )
        .render()
        .menu(),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "half"}) & filters.StateFilter("fin_select_donater"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _select_half(ans: bots.SimpleBotEvent):
    payload = ujson.loads(ans.object.object.message.payload)
    await ans.answer(
        "Выберите студента, сдавшего деньги",
        keyboard=kbs.finances.IncomeNavigator(
            students.get_system_id_of_student(ans.object.object.message.from_id),
        )
        .render()
        .submenu(payload["half"]),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "letter"}) & filters.StateFilter("fin_select_donater"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _select_letter(ans: bots.SimpleBotEvent):
    payload = ujson.loads(ans.object.object.message.payload)
    letter = payload["value"]
    await ans.answer(
        "Список студентов на букву {0}".format(letter),
        keyboard=kbs.finances.IncomeNavigator(
            students.get_system_id_of_student(ans.object.object.message.peer_id),
        )
        .render()
        .students(letter),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "student"}) & filters.StateFilter("fin_select_donater"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _select_student(ans: bots.SimpleBotEvent):
    payload = ujson.loads(ans.object.object.message.payload)
    student_id = students.get_system_id_of_student(ans.object.object.message.from_id)
    state_storage = managers.StateStorageManager(student_id)
    state_storage.update(state=state_storage.get_id_of_state("fin_enter_donate_sum"))

    redis = await aioredis.create_redis_pool("redis://localhost")
    await redis.hmset_dict(
        "add_income:{0}".format(ans.object.object.message.peer_id),
        payer=payload.get("student_id"),
    )
    redis.close()
    await redis.wait_closed()
    await ans.answer("Введите сумму дохода", keyboard=kbs.common.empty())


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_enter_donate_sum"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _save_donate(ans: bots.SimpleBotEvent):
    text = ans.object.object.message.text
    if re.match(r"^\d+$", text):
        fin_store = managers.FinancialConfigManager(
            students.get_system_id_of_student(ans.object.object.message.from_id),
        )
        mention_store = managers.MentionStorageManager(
            students.get_system_id_of_student(ans.object.object.message.from_id),
        )

        redis = await aioredis.create_redis_pool("redis://localhost")
        payer = await redis.hget(
            "add_income:{0}".format(ans.object.object.message.peer_id),
            "payer",
            encoding="utf-8",
        )
        redis.close()
        await redis.wait_closed()

        finances.add_or_edit_donate(
            fin_store.get_or_create().financial_category.id,
            payer,
            int(text),
        )
        mention_store.clear()
        await ans.answer("Доход сохранен", keyboard=kbs.finances.fin_category())
    else:
        await ans.answer("Введите только число")


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "show_debtors"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _call_debtors(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.object.object.message.from_id)
    group_id = admin.get_active_group(admin_id)
    state_store = managers.StateStorageManager(admin_id)
    admin_store = managers.AdminConfigManager(admin_id)
    fin_store = managers.FinancialConfigManager(admin_id)
    with orm.db_session:
        if chats_utils.get_list_of_chats_by_group(group_id):
            category_id = fin_store.get_or_create().financial_category.id
            msgs = generate_debtors_call(category_id)
            state_store.update(
                state=state_store.get_id_of_state("fin_confirm_debtors_call")
            )
            chat_id = admin_store.get_active_chat().vk_id
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
async def _select_chat_debtors(ans: bots.SimpleBotEvent):
    kb = await kbs.common.list_of_chats(
        students.get_system_id_of_student(ans.object.object.message.from_id),
    )
    await ans.answer("Выберите чат", keyboard=kb.get_keyboard())


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_confirm_debtors_call"),
    filters.PLFilter({"button": "chat"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _save_chat_debtors(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.object.object.message.from_id)
    payload = ujson.loads(ans.object.object.message.payload)
    admin_store = managers.AdminConfigManager(admin_id)
    admin_store.update(active_chat=payload["chat_id"])
    await _call_debtors(ans)


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_confirm_debtors_call"),
    filters.PLFilter({"button": "confirm"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _confirm_call_debtors(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.object.object.message.from_id)
    admin_store = managers.AdminConfigManager(admin_id)
    state_store = managers.StateStorageManager(admin_id)
    fin_store = managers.FinancialConfigManager(admin_id)
    msgs = generate_debtors_call(fin_store.get_or_create().financial_category.id)

    with orm.db_session:
        chat = admin_store.get_active_chat().vk_id

    state_store.update(state=state_store.get_id_of_state("main"))
    for msg in msgs:
        await api_context.messages.send(peer_id=chat, message=msg, random_id=0)
    await ans.answer("Призыв отправлен", keyboard=kbs.finances.fin_category())


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_confirm_debtors_call"),
    filters.PLFilter({"button": "deny"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _deny_call_debtors(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.object.object.message.from_id)
    state_store = managers.StateStorageManager(admin_id)
    state_store.update(state=state_store.get_id_of_state("main"))
    await ans.answer("Отправка отменена", keyboard=kbs.finances.fin_category())


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "add_expense"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _add_expense(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.object.object.message.from_id)
    state_store = managers.StateStorageManager(admin_id)
    state_store.update(state=state_store.get_id_of_state("fin_enter_expense_sum"))
    await ans.answer("Введите сумму расхода")


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_enter_expense_sum"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _save_expense(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.object.object.message.from_id)
    text = ans.object.object.message.text
    if re.match(r"^\d+$", text):
        fin_store = managers.FinancialConfigManager(admin_id)
        finances.add_expense(fin_store.get_or_create().financial_category.id, int(text))
        state_store = managers.StateStorageManager(admin_id)
        state_store.update(state=state_store.get_id_of_state("main"))
        await ans.answer("Расход сохранен", keyboard=kbs.finances.fin_category())
    else:
        await ans.answer("Введите только число")


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "show_stats"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _get_statistics(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.object.object.message.from_id)
    fin_store = managers.FinancialConfigManager(admin_id)
    with orm.db_session:
        donates_summ = finances.calculate_incomes_in_category(
            fin_store.get_or_create().financial_category
        )
        expenses_summ = finances.calculate_expenses_in_category(
            fin_store.get_or_create().financial_category
        )
    await ans.answer(
        "Статистика\nСобрано: {0} руб.\nПотрачено: {1} руб.".format(
            donates_summ,
            expenses_summ,
        ),
    )
