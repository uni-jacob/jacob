from database import utils
from database.models import Student


async def generate_message(from_id: int):
    """
    Генерирует сообщение для призыва
    Args:
        from_id: Идентификатор пользователя, из хранилища которого провести генерацию

    Returns:
        str: Сообщение призыва
    """
    user = await utils.get_storage(from_id)
    message = user.text or ""
    students = user.selected_students or ""
    mentions = await generate_mentions(user.names_usage, students)
    message = f"{mentions}\n{message}"
    return message


async def generate_mentions(names_usage: bool, students: str):
    """
    Генерирует призыв студентов
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
            st = await Student.get(id=student)
            hint = st.first_name if names_usage else "!"
            mentions.append(f"@id{st.vk_id} ({hint})")
    return sep.join(mentions)
