from tortoise.transactions import in_transaction

from jacob.database import models


async def create_classroom(
    building: int,
    university_id: int,
    **kwargs,
) -> models.Classroom:
    async with in_transaction():
        return await models.Classroom.create(
            building=building,
            university_id=university_id,
            **kwargs,
        )


async def update_classroom(classroom_id: int, **kwargs):
    async with in_transaction():
        await models.Classroom.filter(id=classroom_id).update(
            **kwargs,
        )
