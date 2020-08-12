import logging

from playhouse.shortcuts import update_model_from_dict

from database.models import Administrator
from database.models import CachedChat
from database.models import Chat
from database.models import State
from database.models import Storage
from database.models import Student
from services.exceptions import BotStateNotFound
from services.exceptions import StudentNotFound
from services.exceptions import UserIsNotAnAdministrator


def _generate_list(data) -> list:
    items = [item for item in data]
    if items:
        return items


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
    student = Student.get_or_none(vk_id=vk_id)
    if student is not None:
        return student.id
    raise StudentNotFound(f"Студента с id ВКонтакте {vk_id} не существует в системе")


def is_user_admin(admin_id: int) -> bool:
    """
    Проверяет, является ли студент администратором
    Args:
        admin_id: идентификатор студента в системе

    Returns:
        bool: статус администрирования студента
    """
    admin = Administrator.get_or_none(id=admin_id)
    if admin is not None:
        return True
    raise UserIsNotAnAdministrator(f"Студент с {admin_id=} не является администратором")


def get_admin_feud(admin_id: int) -> int:
    """
    Возвращает идентификатор группы в которой пользователь является администратором
    Args:
        admin_id: идентификатор администратора

    Returns:
        int: идентификатор группы
    """
    if is_user_admin(admin_id):
        admin = Administrator.get_or_none(id=admin_id)
        return admin.group_id


def get_admin_storage(admin_id: int) -> Storage:
    """
    Ищет хранилище администратора и возвращет объект класса Storage.
    Если хранилище не было найдено, оно создается
    Args:
        admin_id: идентификатор администратора
    Returns:
        Storage: объект хранилища пользователя
    """
    if is_user_admin(admin_id):
        return Storage.get_or_create(id=admin_id)[0]


def update_admin_storage(admin_id: int, **kwargs) -> Storage:
    """
    Обновляет хранилище администратора и возвращает объект хранилища
    Args:
        admin_id: идентификатор администратора
        **kwargs: поля для обновления

    Returns:
        Storage: объект хранилища
    """
    a_id = update_model_from_dict(get_admin_storage(admin_id), kwargs).save()
    return get_admin_storage(a_id)


def clear_admin_storage(admin_id: int) -> Storage:
    """
    Очищает хранилище администратора
    Args:
        admin_id: идентификатор администратора

    Returns:
        Storage: объект хранилища
    """
    return update_admin_storage(
        admin_id,
        state_id=1,
        mailing_id=None,
        selected_students="",
        text="",
        attaches="",
    )


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
    students = [student for student in query]
    if students:
        return students
    raise StudentNotFound(f"В группе {group_id} нет активных студентов")


def get_or_create_cached_chat(chat_id: int) -> CachedChat:
    """
    Возвращает кешированный чат (уже существовавщий или свжесозданный)
    Args:
        chat_id: идентификатор чата ВК

    Returns:
        CachedChat: объект кешированного чата
    """
    return CachedChat.get_or_create(chat_id=chat_id)[0]


def get_id_of_state(description: str = "main") -> int:
    """
    Возвращает идентификатор состояния бота по его описанию
    Если описание не передано - возвращает 1 (идентификатор статуса "main")
    Args:
        description: описание статуса бота

    Returns:
        int: идентфикатор статуса бота

    Raises:
        BotStateNotFound: если переданный статус бота не был найден в БД
    """
    state = State.get_or_none(description=description)
    if state is not None:
        return state.id
    raise BotStateNotFound(f'Статус "{description}" не существует')


def get_unique_second_name_letters_in_a_group(vk_id: int) -> list:
    """
    Возвращает список первых букв фамилий в группе, в которой vk_id является
    администратором
    Args:
        vk_id: Идентификатор пользователя

    Returns:
        list: список первых букв фамилий
    """
    admin_group = get_admin_feud(get_system_id_of_student(vk_id))
    query = (
        Student.select(Student.second_name)
        .where(Student.group_id == admin_group)
        .order_by(Student.second_name)
        .distinct()
    )
    snd_names = [name.second_name[0] for name in query]
    if snd_names:
        return list(dict.fromkeys(snd_names))


def get_list_of_students_by_letter(letter, vk_id):
    """
    Возвращает объекты студентов группы, в которой vk_id администратор, фамилии
    которых начинаются на letter
    Args:
        letter: первая буква фамилий
        vk_id: идентификатор пользователся

    Returns:
        list[Student]: список студентов
    """
    admin_group = get_admin_feud(get_system_id_of_student(vk_id))
    query = (
        Student.select()
        .where(
            (Student.second_name.startswith(letter)) & (Student.group_id == admin_group)
        )
        .order_by(Student.second_name.asc())
    )
    return _generate_list(query)


def get_list_of_chats_by_group(vk_id: int):
    """
    Возвращает список чатов группы, в которой vk_id администратор
    Args:
        vk_id: идентификатор пользователя

    Returns:
        list[Chat]: список объектов чатов
    """
    admin_group = get_admin_feud(get_system_id_of_student(vk_id))
    query = Chat.select().where(group=admin_group)
    return _generate_list(query)


def get_cached_chats():
    """
    Возвращает список кешированных чатов

    Returns:
        list[CachedChat]: список всех чатов, находящихся в кеше
    """
    query = CachedChat.select()
    return _generate_list(query)


def is_chat_registered(vk_id: int, chat_type: int):
    """
    Проверяет, был ли зарегистрирован чат типа chat_type в группе, в которой
    пользователь с vk_id администратор
    Args:
        vk_id: идентификатор пользователя
        chat_type: тип чата

    Returns:
        bool: флаг, указывающий на регистрацию чата
    """
    admin_group = get_admin_feud(get_system_id_of_student(vk_id))
    query = Chat.select().where(
        (Chat.group_id == admin_group) & (Chat.chat_type == chat_type)
    )
    if _generate_list(query):
        return True
    return False


def get_list_of_calling_students(admin_id: int):
    """
    Возвращает список призываемых студентов из хранилища администратора admin_id
    Args:
        admin_id: идентификатор администратора

    Returns:
        list[int]: список призываемых
    """
    store = get_admin_storage(admin_id)
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
    return update_admin_storage(
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


def find_chat(**kwargs):
    """
    ищет зарегистрированный чат
    Args:
        **kwargs: параметры поиска

    Returns:
        Chat: объект чата
    """
    return Chat.get(**kwargs)


def find_student(**kwargs):
    """
    ищет студента
    Args:
        **kwargs: параметры поиска

    Returns:
        Student: объект студента
    """
    return Student.get(**kwargs)


def get_chat_id(admin_id):
    """
    Получает идентификатор активного чата конкретного администратора
    Args:
        admin_id: идентификатор администратора

    Returns:
        Chat: объект активного чата
    """
    store = get_admin_storage(admin_id)
    return find_chat(
        chat_type=store.current_chat, group_id=find_student(id=store.id).group_id
    )


def invert_names_usage(admin_id: int):
    """
    Изменяет использование имен у администратора
    Args:
        admin_id: идентификатор администратора

    Returns:
        Storage: объект хранилища
    """
    store = get_admin_storage(admin_id)
    state = not store.names_usage
    return update_admin_storage(admin_id, names_usage=state)
