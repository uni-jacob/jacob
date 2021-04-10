"""Утилиты для работы со студентами в базе данных."""
from typing import List, Optional

from pony import orm

from jacob.database import models
from jacob.database.models import AcademicStatus, Admin, Student
from jacob.services import exceptions


@orm.db_session
def is_admin_in_group(student_id: int, group_id: int):
    """
    Является ли студент администратором группы.

    Args:
        student_id: идентификатор студента
        group_id: идентификатор группы

    Returns:
        bool: Админ ли?
    """
    return bool(
        orm.select(
            adm
            for adm in Admin
            if adm.student.id == student_id and adm.group.id == group_id
        ),
    )


@orm.db_session
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


@orm.db_session
def get_active_students(group_id: int) -> List[Student]:
    """
    Возвращает список активных (не отчисленных студентов) конкретной группы.

    Args:
        group_id: идентфикатор группы

    Raises:
        StudentNotFound: Когда в группе нет активных студентов

    Returns:
        list[Student]: набор активных студентов группы
    """
    students = orm.select(
        st for st in Student if st.group == group_id and st.academic_status.id < 5
    )
    if students:
        return students
    raise exceptions.StudentNotFound(
        "В группе {0} нет активных студентов".format(group_id),
    )


@orm.db_session
def get_active_students_by_subgroup(
    group_id: int,
    subgroup: int,
) -> List[Student]:
    """
    Возвращает список активных (не отчисленных студентов) конкретной группы.

    Args:
        group_id: идентификатор группы
        subgroup: номер подгруппы

    Raises:
        StudentNotFound: Когда в группе нет активных студентов

    Returns:
        list[Student]: набор активных студентов группы
    """
    students = orm.select(
        st
        for st in Student
        if st.group == group_id
        and st.academic_status.id < 5
        and st.subgroup == subgroup
    )
    if students:
        return students
    raise exceptions.StudentNotFound(
        "В группе {0}/{1} нет активных студентов".format(group_id, subgroup),
    )


@orm.db_session
def get_students_by_academic_status(
    group_id: int,
    academic_status: int,
) -> List[Student]:
    """
    Возвращает список активных (не отчисленных студентов) конкретной группы.

    Args:
        group_id: идентификатор группы
        academic_status: идентификатор формы обучения

    Raises:
        StudentNotFound: Когда в группе нет активных студентов

    Returns:
        list[Student]: набор активных студентов группы
    """
    students = orm.select(
        st
        for st in Student
        if st.group == group_id and st.academic_status.id == academic_status
    )
    if students:
        return students
    raise exceptions.StudentNotFound(
        "В группе {0} нет студентов на {1} форме обучения".format(
            group_id,
            models.AcademicStatus[academic_status].description,
        ),
    )


@orm.db_session
def get_unique_second_name_letters_in_a_group(
    group_ids: List[int],
) -> Optional[List[str]]:
    """
    Возвращает список первых букв фамилий в указанных группах.

    Args:
        group_ids: Идентификатор группы

    Returns:
        list: список первых букв фамилий
    """

    ids = tuple(group_ids)

    query = orm.select(st.last_name for st in Student if st.group.id in ids)
    snd_names = [name[0] for name in query]
    if snd_names:
        return sorted(dict.fromkeys(snd_names))
    return []


@orm.db_session
def get_list_of_students_by_letter(group_ids: List[int], letter: str) -> List[Student]:
    """
    Возвращает объекты студентов активной группы, фамилии которых начинаются на letter.

    Args:
        group_ids: идентификаторы активных групп
        letter: первая буква фамилий

    Returns:
        list[Student]: список студентов
    """

    ids = tuple(group_ids)

    return orm.select(
        st for st in Student if st.group.id in ids and st.last_name[0] == letter
    ).order_by(Student.last_name)


@orm.db_session
def get_academic_statuses():
    return orm.select(ac for ac in AcademicStatus)
