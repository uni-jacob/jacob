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

    if db.get_ownership_of_admin(user_id):
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
        print(query)
        await db.query(query, *args)
    else:
        raise UserIsNotAnAdministrator(
            f"Пользователь {user_id} не является администратором"
        )


async def get_storage(user_id: int, fields: Union[list, tuple]):
    """
    Возвращает объект хранилища администратора
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
        "select id from states where description=$1", description, fetchone=True
    )
    return query["id"]
