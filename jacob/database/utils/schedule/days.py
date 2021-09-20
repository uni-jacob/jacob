from tortoise.transactions import in_transaction

from jacob.database import models


async def get_days() -> list[models.DayOfWeek]:
    """
    Получает список доступных дней недели

    Returns:
        list[Week]: Объекты дней недели
    """
    async with in_transaction():
        return await models.DayOfWeek.all()
