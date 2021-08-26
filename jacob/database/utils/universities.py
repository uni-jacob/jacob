from tortoise.transactions import in_transaction

from jacob.database import models


async def get_universities() -> list[models.University]:
    """
    Получает список всех университетов.

    Returns:
        list[University]: Список университетов.
    """
    async with in_transaction():
        return await models.University.all()


async def get_university_by_id(university_id: int) -> models.University:
    """
    Получает университет по его ИД.
    Args:
        university_id: ИД университета.

    Returns:
        University: Объект университета.
    """
    async with in_transaction():
        return await models.University.get_or_none(id=university_id)
