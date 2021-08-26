from tortoise.transactions import in_transaction

from jacob.database import models


async def get_universities() -> list[models.University]:
    async with in_transaction():
        return await models.University.all()
