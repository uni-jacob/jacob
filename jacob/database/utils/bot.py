"""Методы для работы с внутренними частями бота."""
from pony import orm

from jacob.database.models import State
from jacob.services.exceptions import BotStateNotFound


@orm.db_session
def get_id_of_state(description: str) -> int:
    """
    Возвращает идентификатор состояния бота по его описанию.

    Args:
        description: описание статуса бота

    Returns:
        int: идентфикатор статуса бота

    Raises:
        BotStateNotFound: если переданный статус бота не был найден в БД
    """
    state = State.get(description=description)
    if state is not None:
        return state.id
    raise BotStateNotFound('Статус "{0}" не существует'.format(description))
