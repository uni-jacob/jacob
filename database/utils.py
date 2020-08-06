from database.models import Administrator
from database.models import CachedChat
from database.models import State
from database.models import Storage
from database.models import Student
from utils.exceptions import BotStateNotFound
from utils.exceptions import StudentNotFound
from utils.exceptions import UserIsNotAnAdministrator


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
    students = Student.get_or_none(group_id=group_id, academic_status__gt=0)
    if students is not None:
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