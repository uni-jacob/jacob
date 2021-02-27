"""Бэкенд модуля 'Сообщить об ошибке'."""

from jacob.database import utils as db
from jacob.database.models import Issue


def get_issue_storage(vk_id: int):
    """Получает хранилище отчёта об ошибке.

    Args:
        vk_id: Идентификатор пользователя

    Returns:
        Issue: объект отчёта об ошибке
    """
    last_issue = Issue.get(author=vk_id)

    if last_issue:
        return last_issue
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
    return Issue[issue_id].set(**kwargs)


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

    return "{0}\n\n{1}\n{2}".format(text, is_admin, store)
