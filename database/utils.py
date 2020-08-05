import os
import urllib.parse as urlparse

from database.models import Administrator
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
        return Storage.get_or_create(id=admin_id)


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


def get_db_credentials() -> dict:
    """
    Создает словарь с учетными данными базы данных из переменной окружения DATABASE_URL
    Returns:
        dict: Учетные данные
    """
    url = urlparse.urlparse(os.getenv("DATABASE_URL"))
    db_creds = {
        "user": url.username,
        "password": url.password,
        "host": url.hostname,
        "port": url.port,
        "database": url.path[1:],
    }

    return db_creds
