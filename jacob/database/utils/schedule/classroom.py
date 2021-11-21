from tortoise.transactions import in_transaction

from jacob.database import models


async def update_or_create_classroom(**kwargs) -> models.Classroom:
    async with in_transaction():
        res = await models.Classroom.update_or_create(**kwargs)
        return res[0]
