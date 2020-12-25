"""Шорткаты для меню Призыва."""

import typing

from loguru import logger

from jacob.database import models
from jacob.database.utils import storages
from jacob.services.logger import config as logger_config

logger.configure(**logger_config.config)


def get_mentioned_students_list(admin_id: int) -> typing.List[int]:
    """Возвращает список призываемых студентов из хранилища администратора admin_id.

    Args:
        admin_id: идентификатор администратора

    Returns:
        list[int]: список призываемых
    """
    store = storages.mention.get_mention_storage(admin_id)
    students = store.selected_students
    return list(map(int, filter(bool, students.split(","))))


def update_mentioned_students_list(
    admin_id: int,
    mentioned_students_list: list,
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


def pop_student_from_mention_list(
    admin_id: int,
    student_id: int,
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


def add_student_to_mention_list(
    admin_id: int,
    student_id: int,
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
