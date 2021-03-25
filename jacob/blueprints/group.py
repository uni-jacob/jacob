"""Блок Студенты."""

from loguru import logger
from pony import orm
from vkwave import bots

from jacob.database import models, redis
from jacob.database.utils import admin, students
from jacob.database.utils.storages import managers
from jacob.services import filters
from jacob.services import keyboard as kbs
from jacob.services.logger import config as logger_config

group_router = bots.DefaultRouter()
logger.configure(**logger_config.config)


@bots.simple_bot_message_handler(
    group_router,
    filters.PLFilter({"button": "group_mgmt"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _start_group(ans: bots.SimpleBotEvent):
    await ans.answer(
        "Меню группы",
        keyboard=kbs.group.group_menu(),
    )


@bots.simple_bot_message_handler(
    group_router,
    filters.PLFilter({"button": "lists"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _start_lists(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    group_id = admin.get_active_group(admin_id).id

    with orm.db_session:
        kb = kbs.group.list_of_lists(group_id)

    await ans.answer(
        "Списки студентов группы",
        keyboard=kb,
    )


@bots.simple_bot_message_handler(
    group_router,
    filters.PLFilter({"button": "create_list"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _create_list(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)

    state_store = managers.StateStorageManager(admin_id)
    state_store.update(state=state_store.get_id_of_state("groups_enter_name_list"))

    await ans.answer(
        "Введите название списка",
        keyboard=kbs.common.cancel().get_keyboard(),
    )


@bots.simple_bot_message_handler(
    group_router,
    filters.PLFilter({"button": "cancel"}),
    filters.StateFilter("groups_enter_name_list"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _cancel_saving_list(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    state_store = managers.StateStorageManager(admin_id)
    state_store.update(state=state_store.get_id_of_state("main"))
    await ans.answer(
        "Создание списка отменено",
        keyboard=kbs.group.list_of_lists(admin.get_active_group(admin_id).id),
    )


@bots.simple_bot_message_handler(
    group_router,
    filters.StateFilter("groups_enter_name_list"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _confirm_saving_list(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)

    with orm.db_session:
        models.List(group=admin.get_active_group(admin_id), name=ans.text)

    state_store = managers.StateStorageManager(admin_id)
    state_store.update(state=state_store.get_id_of_state("main"))

    await ans.answer("Список создан")
    await _start_lists(ans)


@bots.simple_bot_message_handler(
    group_router,
    filters.PLFilter({"button": "list"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _list_menu(ans: bots.SimpleBotEvent):
    list_id = ans.payload.get("list")

    with orm.db_session:
        list_name = models.List[list_id].name

    admin_id = students.get_system_id_of_student(ans.from_id)
    state_store = managers.StateStorageManager(admin_id)
    state_store.update(state=state_store.get_id_of_state("groups_select_students"))

    await redis.hmset(
        "current_list:{0}".format(ans.from_id),
        list_id=list_id,
    )

    await ans.answer(
        "Меню списка {0}".format(list_name), keyboard=kbs.group.list_menu()
    )


@bots.simple_bot_message_handler(
    group_router,
    filters.PLFilter({"button": "rename_list"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _start_renaming_list(ans: bots.SimpleBotEvent):

    admin_id = students.get_system_id_of_student(ans.from_id)
    state_store = managers.StateStorageManager(admin_id)
    state_store.update(state=state_store.get_id_of_state("groups_rename_list"))

    await ans.answer(
        "Введите новое имя списка", keyboard=kbs.common.cancel().get_keyboard()
    )


@bots.simple_bot_message_handler(
    group_router,
    filters.PLFilter({"button": "cancel"}),
    filters.StateFilter("groups_rename_list"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _cancel_renaming_list(ans: bots.SimpleBotEvent):
    admin_id = students.get_system_id_of_student(ans.from_id)
    state_store = managers.StateStorageManager(admin_id)
    state_store.update(state=state_store.get_id_of_state("main"))

    await ans.answer("Переименование отменено", keyboard=kbs.group.list_menu())


@bots.simple_bot_message_handler(
    group_router,
    filters.StateFilter("groups_rename_list"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _save_new_list_name(ans: bots.SimpleBotEvent):
    list_id = await redis.hget("current_list:{0}".format(ans.from_id), "list_id")
    admin_id = students.get_system_id_of_student(ans.from_id)
    state_store = managers.StateStorageManager(admin_id)
    state_store.update(state=state_store.get_id_of_state("main"))

    with orm.db_session:
        models.List[list_id].set(name=ans.text)

    await ans.answer("Список переименован", keyboard=kbs.group.list_menu())
