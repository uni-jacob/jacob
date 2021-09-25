from tortoise.transactions import in_transaction

from jacob.database import models


async def get_subjects(group_id: int) -> list[models.Subject]:
    async with in_transaction():
        return await models.Subject.filter(group_id=group_id)
