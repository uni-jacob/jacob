from database import utils as db
from database.models import Student


def generate_mentions(names_usage: bool, students: str) -> str:
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
    for student in students.split(","):
        if student:
            st = Student.get(id=int(student))
            hint = st.first_name if names_usage else "!"
            mentions.append(f"@id{st.vk_id} ({hint})")
    return sep.join(mentions)


def generate_message(admin_id: int) -> str:
    """
    Генерирует сообщение для призыва.

    Args:
        admin_id: Идентификатор пользователя, из хранилища которого провести генерацию

    Returns:
        str: Сообщение призыва
    """
    store = db.admin.get_admin_storage(admin_id)
    message = store.text or ""
    students = store.selected_students or ""
    mentions = generate_mentions(store.names_usage, students)
    return f"{mentions}\n{message}"
