"""Утилиты для работы со студентами в базе данных."""

import typing

from jacob.database.models import Student
from jacob.database.utils import admin
from jacob.services import exceptions


def get_system_id_of_student(vk_id: int) -> int:
    """
    Возвращает идентификатор студента в системе.

    Args:
        vk_id: идентификатор студента в ВКонтакте

    Returns:
        int: идентификатор студента в системе

    Raises:
        StudentNotFound: когда студент с указанным идентификатором ВК не найден в системе
    """
    student = Student.get(vk_id=vk_id)
    if student is not None:
        return student.id
    raise exceptions.StudentNotFound(
        "Студента с id ВКонтакте {0} не существует в системе".format(vk_id),
    )


def get_active_students(group_id: int) -> typing.List[Student]:
    """
    Возвращает список активных (не отчисленных студентов) конкретной группы.

    Args:
        group_id: идентфикатор группы

    Raises:
        StudentNotFound: Когда в группе нет активных студентов

    Returns:
        list[Student]: набор активных студентов группы
    """
    students = Student.select(
        Student.group_id == group_id,
        Student.academic_status > 0,
    )
    if students:
        return students
    raise exceptions.StudentNotFound(
        "В группе {0} нет активных студентов".format(group_id),
    )


def get_unique_second_name_letters_in_a_group(group_id: int) -> list:
    """
    Возвращает список первых букв фамилий в активной группе.

    Args:
        group_id: Идентификатор группы

    Returns:
        list: список первых букв фамилий
    """
    query = (
        Student.select(Student.second_name)
        .where(Student.group_id == group_id)
        .order_by(Student.second_name)
        .distinct()
    )
    snd_names = [name.second_name[0] for name in query]
    if snd_names:
        return list(dict.fromkeys(snd_names))


def get_list_of_students_by_letter(admin_id: int, letter: str) -> typing.List[Student]:
    """
    Возвращает объекты студентов активной группы, фамилии которых начинаются на letter.

    Args:
        admin_id: идентификатор пользователся
        letter: первая буква фамилий

    Returns:
        list[Student]: список студентов
    """
    active_group = admin.get_active_group(admin_id)
    return (
        Student.select()
        .where(
            (Student.second_name.startswith(letter))
            & (Student.group_id == active_group),
        )
        .order_by(Student.second_name.asc())
    )
