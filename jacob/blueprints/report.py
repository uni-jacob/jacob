"""Обработка событий. Блок 'Сообщить об ошибке'."""

import os

from github import Github
from loguru import logger
from vkwave import api, bots, client

from jacob.database.utils import students
from jacob.database.utils.storages import managers
from jacob.services import filters
from jacob.services import keyboard as kbs
from jacob.services.logger import config as logger_config

report_router = bots.DefaultRouter()
api_session = api.API(tokens=os.getenv("VK_TOKEN"), clients=client.AIOHTTPClient())
api_context = api_session.get_context()
logger.configure(**logger_config.config)


@bots.simple_bot_message_handler(
    report_router,
    filters.PLFilter({"button": "report_error"}),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _start_reporting(ans: bots.SimpleBotEvent):
    state_manager = managers.StateStorageManager(
        students.get_system_id_of_student(ans.object.object.message.from_id)
    )
    state_manager.update(
        state=state_manager.get_id_of_state("report_wait_title"),
    )
    await ans.answer(
        "Отправьте заголовок проблемы, кратко описывающий произошедшее",
        keyboard=kbs.common.empty(),
    )


@bots.simple_bot_message_handler(
    report_router,
    filters.StateFilter("report_wait_title"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _ask_for_issue_text(ans: bots.SimpleBotEvent):
    issue_store = managers.IssueStorageManager(
        students.get_system_id_of_student(
            ans.object.object.message.from_id,
        )
    )
    logger.debug(ans.object.object.message.text)
    issue_store.update(
        title=ans.object.object.message.text,
    )
    state_manager = managers.StateStorageManager(
        students.get_system_id_of_student(ans.object.object.message.from_id)
    )
    state_manager.update(
        state=state_manager.get_id_of_state("report_wait_text"),
    )

    await ans.answer("Отправьте текст проблемы с подробным описанием бага")


@bots.simple_bot_message_handler(
    report_router,
    filters.StateFilter("report_wait_text"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _create_issue(ans: bots.SimpleBotEvent):

    gith = Github(os.getenv("GITHUB_TOKEN"))
    repo = gith.get_repo("uni-jacob/jacob")

    issue_store = managers.IssueStorageManager(
        students.get_system_id_of_student(
            ans.object.object.message.from_id,
        )
    )
    issue_store.update(
        text=ans.object.object.message.text,
    )

    new_issue = repo.create_issue(
        title=issue_store.get_or_create().title,
        body=issue_store.generate_issue_text(),
        labels=["report"],
    )

    state_manager = managers.StateStorageManager(
        students.get_system_id_of_student(ans.object.object.message.from_id)
    )
    state_manager.update(
        state=state_manager.get_id_of_state("main"),
    )

    await ans.answer(
        "Ишью создан: https://github.com/dadyarri/jacob/issues/{0}".format(
            new_issue.number,
        ),
        keyboard=kbs.main.main_menu(
            students.get_system_id_of_student(
                ans.object.object.message.from_id,
            ),
        ),
    )
