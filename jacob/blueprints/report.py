"""Обработка событий. Блок 'Сообщить об ошибке'."""

import os

from github import Github
from loguru import logger
from vkwave import api, bots, client

from jacob.database.utils import admin, bot, report, students
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
    state_manager = managers.StateStorageManager(students.get_system_id_of_student(ans.object.object.message.from_id))
    state_manager.update(
        state_id=bot.get_id_of_state("wait_issue_title"),
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
    issue = report.get_or_create_last_issue_of_user(
        ans.object.object.message.from_id,
    )
    report.update_issue(
        issue.id,
        title=ans.object.object.message.text,
    )
    admin.update_admin_storage(
        students.get_system_id_of_student(ans.object.object.message.from_id),
        state_id=bot.get_id_of_state("wait_issue_text"),
    )

    await ans.answer("Отправьте текст проблемы с подробным описанием бага")


@bots.simple_bot_message_handler(
    report_router,
    filters.StateFilter("report_wait_text"),
    bots.MessageFromConversationTypeFilter("from_pm"),
)
async def _create_issue(ans: bots.SimpleBotEvent):

    gith = Github(os.getenv("GITHUB_TOKEN"))
    repo = gith.get_repo("dadyarri/jacob")

    issue = report.get_or_create_last_issue_of_user(
        ans.object.object.message.from_id,
    )
    report.update_issue(
        issue.id,
        text=ans.object.object.message.text,
    )

    new_issue = repo.create_issue(
        title=issue.title,
        body=report.generate_issue_text(
            ans.object.object.message.from_id,
        ),
    )

    admin.clear_admin_storage(
        students.get_system_id_of_student(ans.object.object.message.from_id),
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
