import os
from typing import Union

from database import Database
from utils.exceptions import UserIsNotAnAdministrator

db = Database(os.environ["DATABASE_URL"])


async def update_storage(user_id: int, **kwargs):
    """
    Обновляет хранилище администратора
    Args:
        user_id: Идентификатор пользователя

    Raises:
        UserIsNotAnAdministrator: Если указанный пользователь не является
        администратором
    """
    if await db.get_ownership_of_admin(user_id):
        admin_id = await db.get_user_id(user_id)
        arg_no = 0
        args = []
        query = "UPDATE storage SET"
        for k, v in kwargs.items():
            arg_no += 1
            args.append(v)
            query += f" {k}=${arg_no}"
            if arg_no < len(kwargs):
                query += ","
        arg_no += 1
        args.append(user_id)
        query += f" WHERE id=${arg_no}"
        await db.query(query, *args)
    else:
        raise UserIsNotAnAdministrator(
            f"Пользователь {user_id} не является администратором"
        )


async def get_storage(user_id: int, fields: Union[list, tuple]):
    """
    Возвращает словарь с выбранными полями из хранилища администратора
    Args:
        user_id: Идентфикатор администратора
        fields: Поля, которые нужно вернуть в результате

    Returns:
        dict: Поля из хранилища администратора
    """
    query = await db.query(
        "SELECT $1 FROM storage WHERE id=$2;", ", ".join(fields), user_id, fetchone=True
    )
    return dict(query)


async def clear_storage(user_id: int):
    """
    Очищает хранилище администратора

    Args:
        user_id: Идентификатор пользователя
    """
    await update_storage(
        user_id, mailing_id=None, selected_students="", text="", attaches=""
    )


async def get_id_of_state(description: str = "main"):
    """
    Воззвращает идентификатор состояния по описанию
    Args:
        description: Описание состояния

    Returns:
        int: Идентификатор состояния
    """
    query = await db.query(
        "select id from states where description=$1", description, fetch="one"
    )
    return query["id"]


async def save_chat_to_cache(chat_id: int):
    """
    Сохраняет чат в кеш и возвращает идентификатор сохранённого чата в системе
    Если чат с таким идентификатором уже существует, тогда идентификатор чата в системе
    возвращается сразу
    Args:
        chat_id: Идентификатор чата в ВК

    Returns:
        int: Идентификатор чата в системе
    """
    query = await db.query(
        "SELECT id FROM cached_chats where chat_id=$1", chat_id, fetch="one"
    )
    if query is not None:
        return query["id"]
    query = await db.query(
        "INSERT INTO cached_chats (chat_id) VALUES ($1) RETURNING id",
        chat_id,
        fetch="one",
    )
    return query["id"]


async def delete_chat_from_cache(chat_id):
    """
    Удаление чата из кеша
    Args:
        chat_id: Идентификатор чата ВК
    """
    await db.query("DELETE FROM cached_chats WHERE chat_id=$1", chat_id)


async def find_student(fetch: str, st_id: int):
    """
    Ищет объект студента по набору условий, разделёнными AND
    Args:
        fetch: Тип метода для сборба данных
        st_id: Идентификатор студента в системе

    Returns:
        Record or list[Record]: Найденные записи
    """
    query = await db.query("SELECT * FROM students WHERE id=$1", st_id, fetch=fetch)
    return query


async def find_chat(fetch: str, chat_type: int, group_id: int):
    """
    Ищет объект чата по набору условий, разделёнными AND
    Args:
        fetch: Тип метода для сборба данных
        chat_type: Тип чата
        group_id: Идентификатор группы

    Returns:
        Record or list[Record]: Найденные записи
    """
    query = await db.query(
        "SELECT * FROM chats WHERE chat_type=$1 AND group_id=$2",
        chat_type,
        group_id,
        fetch=fetch,
    )
    return query


async def update_chat_activity(new: bool, **kwargs):
    """
    Обновляет настройки чата
    Args:
        new: Новый статус активности чата
        **kwargs: Параметры для поиска чата и изменения его настроек
    """
    cond = []
    for k, v in kwargs.items():
        cond.append(f"{k}={v}")
    await db.query(
        "UPDATE chats SET is_active=$1 WHERE $2 RETURNING chat_type",
        new,
        " AND ".join(cond),
        fetch="one",
    )


async def bind_chat(
    chat_id: int, group_id: int, chat_type: int, is_active: bool = False
):
    """
    Регистрирует чат
    Args:
        chat_id: Идентификатор чата ВК
        group_id: Идентификатор группы
        chat_type: Тип чата
        is_active: Активность чата для рассылок

    Returns:
        int: Идентификатор чата в системе
    """
    await db.query(
        "INSERT INTO chats (chat_id, group_id, chat_type, is_active) "
        "VALUES ($1, $2, $3, $4)",
        chat_id,
        group_id,
        chat_type,
        is_active,
    )


async def unbind_chat(**kwargs):
    """
    Удаляет чат из зарегистрированных
    Args:
        **kwargs: Набор условий для поиска чата
    """
    cond = []
    for k, v in kwargs.items():
        cond.append(f"{k}={v}")
    await db.query("DELETE FROM chats WHERE $1", " AND ".join(cond))
