"""Утилиты БД для работы с университетом."""

from pony import orm

from jacob.database import models


@orm.db_session
def get_all() -> orm.core.Query:
    """Получает список всех доступных университетов.

    Returns:
        orm.core.Query: Результаты запроса к БД университетов
    """
    return orm.select(uni for uni in models.AlmaMater)
