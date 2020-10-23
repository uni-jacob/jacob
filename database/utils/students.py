import typing as t

from database.models import Student
from database.utils import admin
from database.utils import shortcuts
from services.exceptions import StudentNotFound


def get_system_id_of_student(vk_id: int) -> int:
    """
    Возвращает идентификатор студента в системе.

    Args:
        vk_id: идентификатор студента в ВКонтакте

    Returns:
        int: идентификатор студента в системе

    Raises:
        StudentNotFound: когда студент с указанным идентификатором ВК не найден в
        системе
    """
    student = Student.get_or_none(vk_id=vk_id)
    if student is not None:
        return student.id
    raise StudentNotFound(f"Студента с id ВКонтакте {vk_id} не существует в системе")


def get_active_students(group_id: int) -> t.List[Student]:
    """
    Возвращает список активных (не отчисленных студентов) конкретной группы.

    Args:
        group_id: идентфикатор группы

    Raises:
        StudentNotFound: Когда в группе нет активных студентов

    Returns:
        list[Student]: набор активных студентов группы
    """
    query = Student.select().where(
        Student.group_id == group_id,
        Student.academic_status > 0,
    )
    students = shortcuts.generate_list(query)
    if students:
        return students
    raise StudentNotFound(f"В группе {group_id} нет активных студентов")


def get_unique_second_name_letters_in_a_group(admin_id: int) -> list:
    """
    Возвращает список первых букв фамилий в активной группе.

    Args:
        admin_id: Идентификатор пользователя

    Returns:
        list: список первых букв фамилий
    """
    admin_group = admin.get_active_group(admin_id)
    query = (
        Student.select(Student.second_name)
        .where(Student.group_id == admin_group)
        .order_by(Student.second_name)
        .distinct()
    )
    snd_names = [name.second_name[0] for name in query]
    if snd_names:
        return list(dict.fromkeys(snd_names))


def get_list_of_students_by_letter(admin_id: int, letter: str) -> t.List[Student]:
    """
    Возвращает объекты студентов активной группы, фамилии которых начинаются на letter.

    Args:
        admin_id: идентификатор пользователся
        letter: первая буква фамилий

    Returns:
        list[Student]: список студентов
    """
    active_group = admin.get_active_group(admin_id)
    query = (
        Student.select()
        .where(
            (Student.second_name.startswith(letter))
            & (Student.group_id == active_group),
        )
        .order_by(Student.second_name.asc())
    )
    return shortcuts.generate_list(query)
