from database.utils import admin
from database.utils import chats
from database.utils import students
from services.exceptions import ChatNotFound


def generate_list(data) -> list:
    items = [item for item in data]
    if items:
        return items


def get_list_of_calling_students(admin_id: int):
    """
    Возвращает список призываемых студентов из хранилища администратора admin_id
    Args:
        admin_id: идентификатор администратора

    Returns:
        list[int]: список призываемых
    """
    store = admin.get_admin_storage(admin_id)
    students = store.selected_students
    return list(map(int, filter(bool, students.split(","))))


def update_calling_list(admin_id: int, calling_list: list):
    """
    Изменяет список призыва
    Args:
        admin_id: идентификатор администратора
        calling_list: список призыва для замены

    Returns:
        Storage: хранилище администратора
    """
    return admin.update_admin_storage(
        admin_id, selected_students=",".join(map(str, calling_list))
    )


def pop_student_from_calling_list(admin_id: int, student_id: int):
    """
    Удаляет студента из списка призываемых студентов
    Args:
        admin_id: идентификатор администратора
        student_id: идентфикатор удаляемого студента

    Returns:
        Storage: хранилище администратора
    """
    cl = get_list_of_calling_students(admin_id)
    cl.remove(student_id)
    return update_calling_list(admin_id, cl)


def add_student_to_calling_list(admin_id: int, student_id: int):
    """
    Добавляет студента в список призываемых студентов
    Args:
        admin_id: идентификатор администратора
        student_id: идентфикатор добавляемого студента

    Returns:
        Storage: хранилище администратора
    """
    cl = get_list_of_calling_students(admin_id)
    cl.append(student_id)
    return update_calling_list(admin_id, cl)


def get_active_chat(admin_id):
    """
    Получает идентификатор активного чата конкретного администратора
    Args:
        admin_id: идентификатор администратора

    Returns:
        Chat: объект активного чата
    """
    store = admin.get_admin_storage(admin_id)
    return chats.find_chat(
        chat_type=store.current_chat,
        group_id=students.find_student(id=store.id).group_id,
    )


def invert_names_usage(admin_id: int):
    """
    Изменяет использование имен у администратора
    Args:
        admin_id: идентификатор администратора

    Returns:
        Storage: объект хранилища
    """
    store = admin.get_admin_storage(admin_id)
    state = not store.names_usage
    return admin.update_admin_storage(admin_id, names_usage=state)


def invert_current_chat(admin_id):
    """
    Изменяет активный чат администратора
    Args:
        admin_id: идентификатор администратора

    Returns:
        Storage: объект хранилища
    """
    active_chat = get_active_chat(admin_id)
    store = admin.get_admin_storage(admin_id)
    group_id = students.find_student(id=store.id).group_id
    another_type = abs(active_chat.chat_type.id - 1)
    another_chat = chats.find_chat(group_id=group_id, chat_type=another_type)
    if another_chat is not None:
        admin.update_admin_storage(admin_id, current_chat=another_type)
    else:
        raise ChatNotFound(
            f"У группы {group_id} не зарегистрирован"
            f"{chats.find_chat_type(id=another_type)} чат"
        )
