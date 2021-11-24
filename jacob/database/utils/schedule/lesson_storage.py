from tortoise.transactions import in_transaction

from jacob.database import models


async def get_or_create_lesson_storage(user_id: int) -> models.LessonTempStorage:
    async with in_transaction():
        query = await models.LessonTempStorage.get_or_create(user=user_id)
        return query[0]


async def get_lesson_storage(user_id: int) -> models.LessonTempStorage:
    async with in_transaction():
        return await models.LessonTempStorage.get(user=user_id)


async def update_lesson_storage(user_id: int, **kwargs):
    async with in_transaction():
        await models.LessonTempStorage.filter(user=user_id).update(**kwargs)
