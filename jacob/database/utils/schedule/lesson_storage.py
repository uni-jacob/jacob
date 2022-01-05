from tortoise.transactions import in_transaction

from jacob.database import models


async def get_or_create_lesson_storage(user_id: int) -> models.LessonTempStorage:
    async with in_transaction():
        query = (
            await models.LessonTempStorage.filter(user_id=user_id)
            .prefetch_related(
                "week",
                "day",
                "time",
                "subject",
                "teacher",
                "classroom",
                "user",
                "lesson_type",
            )
            .first()
        )
        return query


async def get_lesson_storage(user_id: int) -> models.LessonTempStorage:
    async with in_transaction():
        return await models.LessonTempStorage.get(user_id=user_id)


async def update_lesson_storage(user_id: int, **kwargs):
    async with in_transaction():
        await models.LessonTempStorage.filter(user_id=user_id).update(**kwargs)
