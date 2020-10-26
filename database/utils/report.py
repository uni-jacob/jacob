from database import utils as db
from database.models import Issue


def get_or_create_last_issue_of_user(vk_id: int):
    last_issue = (
        Issue.select().order_by(Issue.id.desc()).where(Issue.from_id == vk_id).limit(1)
    )

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
    Issue.update(**kwargs).where(Issue.id == issue_id).execute()
    return Issue.get_by_id(issue_id)


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
    text = db.report.get_or_create_last_issue_of_user(vk_id).text

    return f"{text}\n\n{is_admin=}\n{store=}"
