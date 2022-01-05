from tortoise.transactions import in_transaction

from jacob.database import models


async def get_weeks() -> list[models.Week]:
    """
    Получает список доступных типов недель

    Returns:
        list[Week]: Объекты недель
    """
    async with in_transaction():
        return await models.Week.all()
