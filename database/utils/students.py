from database.models import Student
from database.utils import admin
from database.utils import shortcuts
from services.exceptions import StudentNotFound
import typing as t


def get_system_id_of_student(vk_id: int) -> int:
    """
    Возвращает идентификатор студента в системе
    Args:
        vk_id: идентификатор студента в ВКонтакте

    Returns:
        int: идентификатор студента в системе

    Raises:
        StudentNotFound: когда студент с указанным идентификатором ВК не найден
        в системе
    """
    student = find_student(vk_id=vk_id)
    if student is not None:
        return student.id
    raise StudentNotFound(f"Студента с id ВКонтакте {vk_id} не существует в системе")


def get_active_students(group_id: int) -> list:
    """
    Возвращает список активных (не отчисленных студентов) конкретной группы
    Args:
        group_id: идентфикатор группы

    Returns:
        list[Student]: набор активных студентов группы
    """
    query = Student.select().where(
        Student.group_id == group_id, Student.academic_status > 0
    )
    students = shortcuts.generate_list(query)
    if students:
        return students
    raise StudentNotFound(f"В группе {group_id} нет активных студентов")


def get_unique_second_name_letters_in_a_group(vk_id: int) -> list:
    """
    Возвращает список первых букв фамилий в группе, в которой vk_id является
    администратором
    Args:
        vk_id: Идентификатор пользователя

    Returns:
        list: список первых букв фамилий
    """
    admin_group = admin.get_admin_feud(get_system_id_of_student(vk_id))
    query = (
        Student.select(Student.second_name)
        .where(Student.group_id == admin_group)
        .order_by(Student.second_name)
        .distinct()
    )
    snd_names = [name.second_name[0] for name in query]
    if snd_names:
        return list(dict.fromkeys(snd_names))


def get_list_of_students_by_letter(letter: str, vk_id: int) -> t.List[Student]:
    """
    Возвращает объекты студентов группы, в которой vk_id администратор, фамилии
    которых начинаются на letter
    Args:
        letter: первая буква фамилий
        vk_id: идентификатор пользователся

    Returns:
        list[Student]: список студентов
    """
    admin_group = admin.get_admin_feud(get_system_id_of_student(vk_id))
    query = (
        Student.select()
        .where(
            (Student.second_name.startswith(letter)) & (Student.group_id == admin_group)
        )
        .order_by(Student.second_name.asc())
    )
    return shortcuts.generate_list(query)


def find_student(**kwargs) -> Student:
    """
    ищет студента
    Args:
        **kwargs: параметры поиска

    Returns:
        Student: объект студента
    """
    return Student.get_or_none(**kwargs)
