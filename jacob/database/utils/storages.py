import typing

from loguru import logger

from jacob.database import models
from jacob.database import utils as db
from jacob.services.logger import config as logger_config

logger.configure(**logger_config.config)


def update_admin_config(admin_id: int, **kwargs) -> models.AdminConfig:
    """Обновляет хранилище администратора и возвращает объект хранилища.

    Args:
        admin_id: идентификатор администратора
        **kwargs: поля для обновления

    Returns:
        models.AdminConfig: объект хранилища
    """

    store = models.AdminConfig[admin_id]
    store.set(**kwargs)
    logger.debug(f"Хранилище id{admin_id} обновлено с {kwargs}")
    return store


def get_mention_storage(admin_id: int) -> models.MentionStorage:
    """Получает хранилище Призыва админа.

    Args:
        admin_id: идентификатор администратора

    Returns:
        models.MentionStorage: Хранилище Призыва
    """
    return models.MentionStorage.get(admin=admin_id)


def get_mentioned_students_list(admin_id: int) -> typing.List[int]:
    """Возвращает список призываемых студентов из хранилища администратора admin_id.

    Args:
        admin_id: идентификатор администратора

    Returns:
        list[int]: список призываемых
    """
    store = get_mention_storage(admin_id)
    students = store.selected_students
    return list(map(int, filter(bool, students.split(","))))


def update_mentioned_students_list(
    admin_id: int, mentioned_students_list: list
) -> models.MentionStorage:
    """Изменяет список призыва.

    Args:
        admin_id: идентификатор администратора
        mentioned_students_list: список призыва для замены

    Returns:
        models.MentionStorage: хранилище администратора
    """
    store = models.MentionStorage.get(admin=admin_id)
    store.set(
        selected_students=",".join(map(str, mentioned_students_list)),
    )
    return store


def pop_student_from_calling_list(
    admin_id: int, student_id: int
) -> models.MentionStorage:
    """Удаляет студента из списка призываемых студентов.

    Args:
        admin_id: идентификатор администратора
        student_id: идентфикатор удаляемого студента

    Returns:
        Storage: хранилище администратора
    """
    mentioned_students = get_mentioned_students_list(admin_id)
    mentioned_students.remove(student_id)
    return update_mentioned_students_list(admin_id, mentioned_students)


def add_student_to_calling_list(
    admin_id: int, student_id: int
) -> models.MentionStorage:
    """Добавляет студента в список призываемых студентов.

    Args:
        admin_id: идентификатор администратора
        student_id: идентфикатор добавляемого студента

    Returns:
        Storage: хранилище администратора
    """
    calling_list = get_mentioned_students_list(admin_id)
    calling_list.append(student_id)
    return update_mentioned_students_list(admin_id, calling_list)


def get_active_chat(admin_id: int) -> models.Chat:
    """Получает объект активного чата конкретного администратора.

    Args:
        admin_id: идентификатор администратора

    Returns:
        Chat: объект активного чата
    """
    store = db.admin.get_or_create_admin_config(admin_id)
    return models.Chat.get_by_id(store.active_chat)


def invert_names_usage(admin_id: int) -> models.AdminConfig:
    """Изменяет использование имен у администратора.

    Args:
        admin_id: идентификатор администратора

    Returns:
        Storage: объект хранилища
    """
    store = db.admin.get_or_create_admin_config(admin_id)
    state = not store.names_usage
    return update_admin_config(admin_id, names_usage=state)
