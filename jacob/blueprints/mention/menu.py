"""Главное меню Призыва."""

import os
import random

import ujson
from loguru import logger
from pony import orm
from vkwave import api, bots, client

from jacob.database import models
from jacob.database.utils import admin, lists, students
from jacob.database.utils.storages import managers
from jacob.services import call, chats, exceptions, filters
from jacob.services import keyboard as kbs
from jacob.services.logger import config as logger_config

call_menu_router = bots.DefaultRouter()
api_session = api.API(
    tokens=os.getenv("VK_TOKEN"),
    clients=client.AIOHTTPClient(),
)
api_context = api_session.get_context()
logger.configure(**logger_config.config)


@bots.simple_bot_message_handler(
    call_menu_router,
    filters.PLFilter({"button": "half"}),
    filters.StateFilter("mention_select_mentioned"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _select_half(ans: bots.SimpleBotEvent):
    payload = ujson.loads(ans.object.object.message.payload)
    admin_id = students.get_system_id_of_student(ans.object.object.message.from_id)
    await ans.answer(
        "Выберите призываемых студентов",
        keyboard=kbs.call.CallNavigator(admin_id).render().submenu(payload["half"]),
    )


@bots.simple_bot_message_handler(
    call_menu_router,
    filters.PLFilter({"button": "letter"}),
    filters.StateFilter("mention_select_mentioned"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _select_letter(ans: bots.SimpleBotEvent):
    payload = ujson.loads(ans.object.object.message.payload)
    letter = payload["value"]
    admin_id = students.get_system_id_of_student(ans.object.object.message.from_id)
    await ans.answer(
        "Список студентов на букву {0}".format(letter),
        keyboard=kbs.call.CallNavigator(admin_id).render().students(letter),
    )


@bots.simple_bot_message_handler(
    call_menu_router,
    filters.PLFilter({"button": "student"}),
    filters.StateFilter("mention_select_mentioned"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _select_student(ans: bots.SimpleBotEvent):
    payload = ujson.loads(ans.object.object.message.payload)
    student_id = payload["student_id"]
    admin_id = students.get_system_id_of_student(ans.object.object.message.peer_id)
    mention_manager = managers.MentionStorageManager(admin_id)
    if student_id in mention_manager.get_mentioned_students():
        mention_manager.remove_from_mentioned(
            student_id,
        )
        label = "удален из списка призыва"
    else:
        mention_manager.append_to_mentioned_students(
            student_id,
        )
        label = "добавлен в список призыва"
    await ans.answer(
        "{0} {1}".format(payload["name"], label),
        keyboard=kbs.call.CallNavigator(
            admin_id,
        )
        .render()
        .students(payload["letter"]),
    )


@bots.simple_bot_message_handler(
    call_menu_router,
    filters.PLFilter({"button": "save_selected"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _confirm_call(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.object.object.message.peer_id)
    msg = call.generate_message(admin_id)

    admin_storage = managers.AdminConfigManager(admin_id)
    mention_storage = managers.MentionStorageManager(admin_id)
    state_storage = managers.StateStorageManager(admin_id)

    with orm.db_session:
        chat_id = admin_storage.get_active_chat().vk_id

    chat_name = await chats.get_chat_name(api_context, chat_id)

    if not msg and not mention_storage.get_attaches():
        raise exceptions.EmptyCallMessage("Сообщение призыва не может быть пустым")
    state_storage.update(
        state=state_storage.get_id_of_state("mention_confirm"),
    )
    await ans.answer(
        'Сообщение будет отправлено в чат "{0}":\n{1}'.format(chat_name, msg),
        keyboard=kbs.call.call_prompt(
            admin_id,
        ),
        attachment=mention_storage.get_attaches() or "",
    )


@bots.simple_bot_message_handler(
    call_menu_router,
    filters.PLFilter({"button": "presets"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _presets(ans: bots.SimpleBotEvent):
    await ans.answer("Список пресетов", keyboard=kbs.call.presets())


@bots.simple_bot_message_handler(
    call_menu_router,
    filters.PLFilter({"button": "subgroups"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _subgroups(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    group_id = admin.get_active_group(admin_id).id

    await ans.answer("Выберите подгруппу", keyboard=kbs.common.subgroups(group_id))


@bots.simple_bot_message_handler(
    call_menu_router,
    filters.PLFilter({"button": "subgroup"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _call_by_subgroup(ans: bots.SimpleBotEvent):
    admin_id: int = students.get_system_id_of_student(ans.from_id)
    with orm.db_session:
        active_students: list[
            models.Student
        ] = students.get_active_students_by_subgroup(
            admin.get_active_group(admin_id),
            ans.payload.get("subgroup"),
        )
        mentioned_list: list[int] = [st.id for st in active_students]
        mention_storage = managers.MentionStorageManager(admin_id)

        if set(mentioned_list).issubset(mention_storage.get_mentioned_students()):
            mention_storage.update_mentioned_students(
                [
                    elem
                    for elem in mention_storage.get_mentioned_students()
                    if elem not in mentioned_list
                ],
            )
            await ans.answer(
                "Все студенты подгруппы {0} удалены из списка Призыва".format(
                    ans.payload.get("subgroup"),
                ),
            )
        else:
            mention_storage.update_mentioned_students(mentioned_list)
            await ans.answer(
                "Все студенты подгруппы {0} выбраны для Призыва".format(
                    ans.payload.get("subgroup"),
                ),
            )


@bots.simple_bot_message_handler(
    call_menu_router,
    filters.PLFilter({"button": "academic_statuses"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _academic_statuses(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    group_id = admin.get_active_group(admin_id).id

    await ans.answer(
        "Выберите форму обучения",
        keyboard=kbs.common.academic_statuses(group_id),
    )


@bots.simple_bot_message_handler(
    call_menu_router,
    filters.PLFilter({"button": "ac_status"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _call_by_ac_status(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    with orm.db_session:
        active_students = students.get_students_by_academic_status(
            admin.get_active_group(admin_id),
            ans.payload.get("status"),
        )
        mentioned_list = [st.id for st in active_students]
        mention_storage = managers.MentionStorageManager(admin_id)
        if set(mentioned_list).issubset(mention_storage.get_mentioned_students()):
            list_ = [
                elem
                for elem in mention_storage.get_mentioned_students()
                if elem not in mentioned_list
            ]
            logger.debug(list_)
            mention_storage.update_mentioned_students(list_)
            await ans.answer(
                "Все студенты {0} формы обучения удалены из списка Призыва".format(
                    models.AcademicStatus[ans.payload.get("status")].description,
                ),
            )
        else:
            mention_storage.update_mentioned_students(mentioned_list)
            await ans.answer(
                "Все студенты {0} формы обучения выбраны для Призыва".format(
                    models.AcademicStatus[ans.payload.get("status")].description,
                ),
            )


@bots.simple_bot_message_handler(
    call_menu_router,
    filters.PLFilter({"button": "call_all"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _call_them_all(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.object.object.message.peer_id)
    with orm.db_session:
        active_students = students.get_active_students(admin.get_active_group(admin_id))
        mentioned_list = [st.id for st in active_students]
        mention_storage = managers.MentionStorageManager(admin_id)
        if set(mentioned_list).issubset(mention_storage.get_mentioned_students()):
            list_ = [
                elem
                for elem in mention_storage.get_mentioned_students()
                if elem not in mentioned_list
            ]
            mention_storage.update_mentioned_students(list_)
            await ans.answer("Все студенты удалены из списка Призыва")
        else:
            mention_storage.update_mentioned_students(mentioned_list)
            await ans.answer("Все студенты выбраны для Призыва")


@bots.simple_bot_message_handler(
    call_menu_router,
    filters.PLFilter({"button": "custom_presets"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _custom_presets(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    group_id = admin.get_active_group(admin_id).id
    await ans.answer(
        "Список пользовательских пресетов",
        keyboard=kbs.common.custom_presets(group_id),
    )


@bots.simple_bot_message_handler(
    call_menu_router,
    filters.PLFilter({"button": "preset"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _call_by_custom_preset(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    with orm.db_session:
        active_students = lists.get_students_in_list(
            ans.payload.get("preset"),
        )
        mentioned_list = [st.id for st in active_students]
        mention_storage = managers.MentionStorageManager(admin_id)
        if set(mentioned_list).issubset(mention_storage.get_mentioned_students()):
            list_ = [
                elem
                for elem in mention_storage.get_mentioned_students()
                if elem not in mentioned_list
            ]
            mention_storage.update_mentioned_students(list_)
            await ans.answer(
                "Все студенты списка {0} удалены из списка Призыва".format(
                    models.List[ans.payload.get("preset")].name,
                ),
            )
        else:
            mention_storage.update_mentioned_students(mentioned_list)
            await ans.answer(
                "Все студенты списка {0} выбраны для Призыва".format(
                    models.List[ans.payload.get("preset")].name,
                ),
            )


@bots.simple_bot_message_handler(
    call_menu_router,
    filters.StateFilter("mention_confirm"),
    filters.PLFilter({"button": "confirm"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _send_call(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.object.object.message.peer_id)

    mention_storage = managers.MentionStorageManager(admin_id)
    admin_storage = managers.AdminConfigManager(admin_id)

    msg = call.generate_message(admin_id)
    bits = 64
    with orm.db_session:
        chat_id = admin_storage.get_active_chat().vk_id
    await api_context.messages.send(
        peer_id=chat_id,
        message=msg,
        random_id=random.getrandbits(bits),
        attachment=mention_storage.get_attaches() or "",
    )
    mention_storage.clear()
    await ans.answer(
        "Сообщение отправлено",
        keyboard=kbs.main.main_menu(admin_id),
    )


@bots.simple_bot_message_handler(
    call_menu_router,
    filters.StateFilter("mention_confirm"),
    filters.PLFilter({"button": "names_usage"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _invert_names_usage(ans: bots.SimpleBotEvent):
    admin_storage = managers.AdminConfigManager(
        students.get_system_id_of_student(ans.object.object.message.from_id),
    )
    admin_storage.invert_names_usage()
    await _confirm_call(ans)


@bots.simple_bot_message_handler(
    call_menu_router,
    filters.StateFilter("mention_confirm"),
    filters.PLFilter({"button": "chat_config"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _select_chat(ans: bots.SimpleBotEvent):
    kb = await kbs.common.list_of_chats(
        api_context,
        students.get_system_id_of_student(ans.object.object.message.from_id),
    )
    await ans.answer("Выберите чат", keyboard=kb.get_keyboard())


@bots.simple_bot_message_handler(
    call_menu_router,
    filters.StateFilter("mention_confirm"),
    filters.PLFilter({"button": "chat"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _change_chat(ans: bots.SimpleBotEvent):
    payload = ujson.loads(ans.object.object.message.payload)
    admin_storage = managers.AdminConfigManager(
        students.get_system_id_of_student(ans.object.object.message.from_id),
    )
    admin_storage.update(
        active_chat=payload["chat_id"],
    )
    await _confirm_call(ans)
