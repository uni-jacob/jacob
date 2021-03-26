from pony import orm

from jacob.database import models


@orm.db_session
def get_lists_of_group(group_id: int):
    return orm.select(gr for gr in models.List if gr.group.id == group_id)


@orm.db_session
def get_students_in_list(list_id: int):
    """Получает список студентов в списке

    Args:
        list_id: Идентификатор списка
    """
    return orm.select(
        item.student for item in models.ListStudents if item.list.id == list_id
    )[:]


@orm.db_session
def is_student_in_list(list_id: int, student_id: int) -> bool:
    """Проверяет находится ли студент в группе.

    Args:
        list_id: Идентификатор списка
        student_id: Идентификатор студента

    Returns:
        bool: Наличие студента в списке
    """
    return models.Student[student_id] in get_students_in_list(list_id)


@orm.db_session
def add_student_to_list(list_id: int, student_id: int):
    """Добавляет студента в список.

    Args:
        list_id: Идентификатор списка
        student_id: Идентификатор студента
    """

    models.ListStudents(list=list_id, student=student_id)


@orm.db_session
def remove_student_from_list(list_id: int, student_id: int):
    """Удаляет студента из списка.

    Args:
        list_id: Идентификатор списка
        student_id: Идентификатор студента
    """

    orm.delete(
        item
        for item in models.ListStudents
        if item.list.id == list_id and item.student.id == student_id
    )
