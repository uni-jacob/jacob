"""Вспомогательные функции Призыва."""

from jacob.database.models import Student
from jacob.database.utils.storages import managers


def generate_mentions(names_usage: bool, students: list) -> str:
    """
    Генерирует призыв студентов.

    Args:
        names_usage: Использование имен студентов
        students: Список идентификаторов призываемых студентов

    Returns:
        str: Призыв студентов
    """
    mentions = []
    sep = ", " if names_usage else ""
    for student in students:
        if student:
            st = Student.get(id=int(student))
            hint = st.first_name if names_usage else "!"
            mentions.append("@id{0} ({1})".format(st.vk_id, hint))
    return sep.join(mentions)


def generate_message(admin_id: int) -> str:
    """
    Генерирует сообщение для призыва.

    Args:
        admin_id: Идентификатор пользователя, из хранилища которого провести генерацию

    Returns:
        str: Сообщение призыва
    """
    mention_storage = managers.MentionStorageManager(admin_id)
    admin_storage = managers.AdminConfigManager(admin_id)

    message = mention_storage.get_text() or ""
    students = mention_storage.get_mentioned_students() or ""
    mentions = generate_mentions(admin_storage.get_names_usage(), students)
    return "\n".join((mentions, message))
