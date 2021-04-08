"""Блок Финансы."""

import os
import re

import ujson
from pony import orm
from vkwave import api, bots, client

from jacob.database import models, redis
from jacob.database.utils import admin, chats, finances, students
from jacob.database.utils.storages import managers
from jacob.services import chats as chat_utils
from jacob.services import filters
from jacob.services import keyboard as kbs
from jacob.services.finances import generate_debtors_call

finances_router = bots.DefaultRouter()
api_session = api.API(tokens=os.getenv("VK_TOKEN"), clients=client.AIOHTTPClient())
api_context = api_session.get_context()


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "finances"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _finances(ans: bots.SimpleBotEvent):
    await ans.answer(
        "Список финансовых категорий",
        keyboard=kbs.finances.list_of_fin_categories(
            students.get_system_id_of_student(ans.from_id),
        ),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "create_finances_category"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _create_category(ans: bots.SimpleBotEvent):
    state_storage = managers.StateStorageManager(
        students.get_system_id_of_student(ans.from_id),
    )
    state_storage.update(state=state_storage.get_id_of_state("fin_wait_category_desc"))
    await ans.answer(
        "Отправьте название категории и сумму сбора, разделенные пробелом",
        keyboard=kbs.common.cancel().get_keyboard(),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_wait_category_desc"),
    filters.PLFilter({"button": "cancel"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _cancel_creating_category(ans: bots.SimpleBotEvent):
    student_id = students.get_system_id_of_student(ans.from_id)
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
        admin_store = managers.AdminConfigManager(student_id)
        fin_store = managers.FinancialConfigManager(student_id)
        fin_store.update(financial_category=category.id)
        state_storage = managers.StateStorageManager(student_id)
        state_storage.update(
            state=state_storage.get_id_of_state("fin_send_alert"),
        )
        with orm.db_session:
            chat_id = admin_store.get_active_chat().vk_id

        chat_title = await chat_utils.get_chat_name(api_context, chat_id)

        await ans.answer(
            "Категория {0} зарегистрирована. Вы можете отправить сообщение о начале сбора в чат {1}".format(
                category.name,
                chat_title,
            ),
            keyboard=kbs.common.confirm_with_chat_update(),
        )
    else:
        await ans.answer("Неверный формат данных")


@bots.simple_bot_message_handler(
    finances_router,
    filters.PayloadFilter({"button": "send_fin_alert"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _offer_alert(ans: bots.SimpleBotEvent):
    student_id = students.get_system_id_of_student(ans.from_id)
    admin_store = managers.AdminConfigManager(student_id)
    state_storage = managers.StateStorageManager(student_id)
    fin_store = managers.FinancialConfigManager(student_id)
    state_storage.update(
        state=state_storage.get_id_of_state("fin_send_alert"),
    )

    with orm.db_session:
        chat_id = admin_store.get_active_chat().vk_id
        category_name = fin_store.get_or_create().financial_category.name

    chat_title = await chat_utils.get_chat_name(api_context, chat_id)

    await ans.answer(
        "Сообщение о начале сбора на {0} будет отправлено в чат {1}".format(
            category_name,
            chat_title,
        ),
        keyboard=kbs.common.confirm_with_chat_update(),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_send_alert"),
    filters.PLFilter({"button": "confirm"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _confirm_send_alarm(ans: bots.SimpleBotEvent):

    student_id = students.get_system_id_of_student(ans.from_id)
    admin_store = managers.AdminConfigManager(student_id)
    state_storage = managers.StateStorageManager(student_id)
    state_storage.update(state=state_storage.get_id_of_state("main"))

    fin_store = managers.FinancialConfigManager(student_id)

    with orm.db_session:
        chat_vk_id = admin_store.get_active_chat().vk_id
        category_name = fin_store.get_or_create().financial_category.name
        category_sum = fin_store.get_or_create().financial_category.summ

    await ans.api_ctx.messages.send(
        peer_id=chat_vk_id,
        random_id=0,
        message="Начат сбор средств на {0}. Сумма {1} руб.".format(
            category_name,
            category_sum,
        ),
    )

    await ans.answer(
        "Сообщение отправлено",
        keyboard=kbs.finances.fin_prefs(),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_send_alert"),
    filters.PLFilter({"button": "deny"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _cancel_send_alarm(ans: bots.SimpleBotEvent):
    student_id = students.get_system_id_of_student(ans.from_id)
    state_storage = managers.StateStorageManager(student_id)
    state_storage.update(state=state_storage.get_id_of_state("main"))
    await ans.answer(
        "Хорошо, уведемление отправлено не будет",
        keyboard=kbs.finances.fin_category(),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_send_alert"),
    filters.PLFilter({"button": "chat_config"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _select_chat_alert(ans: bots.SimpleBotEvent):
    kb = await kbs.common.list_of_chats(
        api_context,
        students.get_system_id_of_student(ans.object.object.message.from_id),
    )
    await ans.answer("Выберите чат", keyboard=kb.get_keyboard())


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_send_alert"),
    filters.PLFilter({"button": "chat"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _send_alert_change_chat(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    admin_store = managers.AdminConfigManager(admin_id)
    admin_store.update(active_chat=ans.payload["chat_id"])
    await _offer_alert(ans)


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "fin_category"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _fin_category_menu(ans: bots.SimpleBotEvent):
    payload = ujson.loads(ans.object.object.message.payload)
    fin_storage = managers.FinancialConfigManager(
        students.get_system_id_of_student(ans.from_id),
    )
    category = payload.get("category")
    if category is not None:
        fin_storage.update(financial_category=category)

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
    student_id = students.get_system_id_of_student(ans.from_id)
    state_storage = managers.StateStorageManager(student_id)
    state_storage.update(state=state_storage.get_id_of_state("fin_select_donater"))
    await ans.answer(
        "Выберите студента, сдавшего деньги",
        keyboard=kbs.finances.IncomeNavigator(
            student_id,
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
    await ans.answer(
        "Выберите студента, сдавшего деньги",
        keyboard=kbs.finances.IncomeNavigator(
            students.get_system_id_of_student(ans.object.object.message.from_id),
        )
        .render()
        .submenu(ans.payload["half"]),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "letter"}) & filters.StateFilter("fin_select_donater"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _select_letter(ans: bots.SimpleBotEvent):
    letter = ans.payload["value"]
    await ans.answer(
        "Список студентов на букву {0}".format(letter),
        keyboard=kbs.finances.IncomeNavigator(
            students.get_system_id_of_student(ans.from_id),
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
    student_id = students.get_system_id_of_student(ans.from_id)
    state_storage = managers.StateStorageManager(student_id)
    state_storage.update(state=state_storage.get_id_of_state("fin_enter_donate_sum"))

    await redis.hmset(
        "add_income:{0}".format(ans.from_id),
        payer=ans.payload.get("student_id"),
    )
    await ans.answer("Введите сумму дохода", keyboard=kbs.common.empty())


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_enter_donate_sum"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _save_donate(ans: bots.SimpleBotEvent):
    if re.match(r"^\d+$", ans.text):
        student_id = students.get_system_id_of_student(ans.from_id)
        fin_store = managers.FinancialConfigManager(
            student_id,
        )
        mention_store = managers.MentionStorageManager(
            student_id,
        )
        state_store = managers.StateStorageManager(
            student_id,
        )
        state_store.update(state=state_store.get_id_of_state("main"))

        payer = await redis.hget(
            "add_income:{0}".format(ans.object.object.message.peer_id),
            "payer",
        )

        finances.add_or_edit_donate(
            fin_store.get_or_create().financial_category.id,
            payer,
            int(ans.text),
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
    admin_id = students.get_system_id_of_student(ans.from_id)
    group_id = admin.get_active_group(admin_id)
    state_store = managers.StateStorageManager(admin_id)
    admin_store = managers.AdminConfigManager(admin_id)
    fin_store = managers.FinancialConfigManager(admin_id)
    with orm.db_session:
        if chats.get_list_of_chats_by_group(group_id):
            category_id = fin_store.get_or_create().financial_category.id
            msgs = generate_debtors_call(category_id)
            state_store.update(
                state=state_store.get_id_of_state("fin_confirm_debtors_call"),
            )
            chat_id = admin_store.get_active_chat().vk_id
            chat_title = await chat_utils.get_chat_name(api_context, chat_id)
            for msg in msgs:
                await ans.answer(msg)
            if len(msgs) > 1:
                text = "Сообщения будут отправлены в {0}"
            else:
                text = "Сообщение будет отправлено в {0}"
            await ans.answer(
                text.format(chat_title),
                keyboard=kbs.common.confirm_with_chat_update(),
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
        api_context,
        students.get_system_id_of_student(ans.from_id),
    )
    await ans.answer("Выберите чат", keyboard=kb.get_keyboard())


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_confirm_debtors_call"),
    filters.PLFilter({"button": "chat"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _save_chat_debtors(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    admin_store = managers.AdminConfigManager(admin_id)
    admin_store.update(active_chat=ans.payload["chat_id"])
    await _call_debtors(ans)


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_confirm_debtors_call"),
    filters.PLFilter({"button": "confirm"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _confirm_call_debtors(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
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
    admin_id = students.get_system_id_of_student(ans.from_id)
    state_store = managers.StateStorageManager(admin_id)
    state_store.update(state=state_store.get_id_of_state("main"))
    await ans.answer("Отправка отменена", keyboard=kbs.finances.fin_category())


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "add_expense"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _add_expense(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    state_store = managers.StateStorageManager(admin_id)
    state_store.update(state=state_store.get_id_of_state("fin_enter_expense_sum"))
    await ans.answer(
        "Введите сумму расхода",
        keyboard=kbs.common.cancel().get_keyboard(),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_enter_expense_sum"),
    filters.PLFilter({"button": "cancel"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _cancel_adding_expense(ans: bots.SimpleBotEvent):
    await ans.answer("Отмена создания расхода", keyboard=kbs.finances.fin_category())


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_enter_expense_sum"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _save_expense(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.object.object.message.from_id)
    if re.match(r"^\d+$", ans.text):
        fin_store = managers.FinancialConfigManager(admin_id)
        finances.add_expense(
            fin_store.get_or_create().financial_category.id,
            int(ans.text),
        )
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
    admin_id = students.get_system_id_of_student(ans.from_id)
    fin_store = managers.FinancialConfigManager(admin_id)
    with orm.db_session:
        category = fin_store.get_or_create().financial_category
        donates_summ = finances.calculate_incomes_in_category(
            category,
        )
        expenses_summ = finances.calculate_expenses_in_category(
            category,
        )
    await ans.answer(
        "Статистика\nСобрано: {0} руб.\nПотрачено: {1} руб.".format(
            donates_summ,
            expenses_summ,
        ),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "finances_pref"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _open_prefs(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    fin_store = managers.FinancialConfigManager(admin_id)

    with orm.db_session:
        category_name = fin_store.get_or_create().financial_category.name

    await ans.answer(
        'Настройки категории "{0}"'.format(category_name),
        keyboard=kbs.finances.fin_prefs(),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "rename_fin_cat"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _rename_category(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    state_store = managers.StateStorageManager(admin_id)
    state_store.update(state=state_store.get_id_of_state("fin_wait_new_name"))
    await ans.answer(
        "Введите новое название категории",
        keyboard=kbs.common.cancel().get_keyboard(),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "cancel"}),
    filters.StateFilter("fin_wait_new_name"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _cancel_renaming_category(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    state_store = managers.StateStorageManager(admin_id)
    state_store.update(state=state_store.get_id_of_state("main"))
    await ans.answer(
        "Переименование отменено",
        keyboard=kbs.finances.fin_prefs(),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_wait_new_name"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _save_new_name_category(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    fin_store = managers.FinancialConfigManager(admin_id)

    with orm.db_session:
        category_id = fin_store.get_or_create().financial_category.id

        models.FinancialCategory[category_id].set(name=ans.text)

    state_store = managers.StateStorageManager(admin_id)
    state_store.update(state=state_store.get_id_of_state("main"))

    await ans.answer(
        "Категория сохранена",
        keyboard=kbs.finances.fin_prefs(),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "change_fin_sum"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _update_category_sum(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    state_store = managers.StateStorageManager(admin_id)
    state_store.update(state=state_store.get_id_of_state("fin_wait_new_sum"))
    await ans.answer(
        "Введите новую сумму сбора",
        keyboard=kbs.common.cancel().get_keyboard(),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.PLFilter({"button": "cancel"}),
    filters.StateFilter("fin_wait_new_sum"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _cancel_changing_sum_of_category(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    state_store = managers.StateStorageManager(admin_id)
    state_store.update(state=state_store.get_id_of_state("main"))
    await ans.answer(
        "Изменение суммы отменено",
        keyboard=kbs.finances.fin_prefs(),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_wait_new_sum"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _save_new_sum_category(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    fin_store = managers.FinancialConfigManager(admin_id)

    if re.match(r"^\d+$", ans.text):

        with orm.db_session:
            category_id = fin_store.get_or_create().financial_category.id
            models.FinancialCategory[category_id].set(summ=ans.text)

        state_store = managers.StateStorageManager(admin_id)
        state_store.update(state=state_store.get_id_of_state("main"))

        await ans.answer(
            "Категория сохранена",
            keyboard=kbs.finances.fin_prefs(),
        )
    else:
        await ans.answer("Неверный формат данных")


@bots.simple_bot_message_handler(
    finances_router,
    filters.PayloadFilter({"button": "delete_fin_cat"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _remove_cat(ans: bots.SimpleBotEvent):
    student_id = students.get_system_id_of_student(ans.from_id)
    state_storage = managers.StateStorageManager(student_id)
    fin_store = managers.FinancialConfigManager(student_id)
    state_storage.update(
        state=state_storage.get_id_of_state("fin_delete_cat"),
    )

    with orm.db_session:
        category_name = fin_store.get_or_create().financial_category.name

    await ans.answer(
        "Удалить категорию {0}?".format(
            category_name,
        ),
        keyboard=kbs.common.prompt().get_keyboard(),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_delete_cat"),
    filters.PLFilter({"button": "confirm"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _confirm_remove_cat(ans: bots.SimpleBotEvent):

    student_id = students.get_system_id_of_student(ans.from_id)
    state_storage = managers.StateStorageManager(student_id)
    state_storage.update(state=state_storage.get_id_of_state("main"))

    fin_store = managers.FinancialConfigManager(student_id)

    with orm.db_session:
        category = fin_store.get_or_create().financial_category
        category.delete()

    await ans.answer(
        "Категория удалена",
        keyboard=kbs.finances.list_of_fin_categories(student_id),
    )


@bots.simple_bot_message_handler(
    finances_router,
    filters.StateFilter("fin_delete_cat"),
    filters.PLFilter({"button": "deny"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _cancel_remove_cat(ans: bots.SimpleBotEvent):
    student_id = students.get_system_id_of_student(ans.from_id)
    state_storage = managers.StateStorageManager(student_id)
    state_storage.update(state=state_storage.get_id_of_state("main"))
    await ans.answer(
        "Отмена",
        keyboard=kbs.finances.fin_prefs(),
    )
