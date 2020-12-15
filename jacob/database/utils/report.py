"""Бэкенд модуля 'Сообщить об ошибке'."""

from pony import orm

from jacob.database import utils as db
from jacob.database.models import Issue


def get_issue_storage(vk_id: int):
    last_issue = Issue.get(author=vk_id)

    if last_issue:
        return last_issue[0]
    return Issue.create(from_id=vk_id)


def update_issue(issue_id: int, **kwargs):
    """
    Обновляет ишью в базе данных.

    Args:
        issue_id: Идентификатор ишью
        **kwargs: Данные для обновления

    Returns:
        Issue: Объект ишью
    """
    issue = Issue.update(**kwargs)
    orm.commit()
    return issue


def generate_issue_text(vk_id: int) -> str:
    """
    Генерирует текст ишью.

    (К сохраненному тексту добавляется служебная информация)

    Args:
        vk_id: Идентификатор ВКонтакте

    Returns:
        str: Текст ишью
    """
    store = db.admin.get_admin_storage(
        db.students.get_system_id_of_student(vk_id),
    ).json()
    is_admin = db.admin.is_user_admin(
        db.students.get_system_id_of_student(vk_id),
    )
    text = db.report.get_issue_storage(vk_id).text

    return f"{text}\n\n{is_admin=}\n{store=}"
