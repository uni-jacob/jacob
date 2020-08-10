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
    raise UserIsNotAnAdministrator(f"Студент с {id=} не является администратором")


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
    return get_admin_storage(admin_id).update(**kwargs)


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
