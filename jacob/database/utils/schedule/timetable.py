from tortoise.transactions import in_transaction

from jacob.database import models


async def get_timetable(university_id: int) -> list[models.Timetable]:
    async with in_transaction():
        return await models.Timetable.filter(university_id=university_id)


async def create_lesson_time(
    university_id: int,
    start_time: str,
    end_time: str,
) -> models.Timetable:
    async with in_transaction():
        return await models.Timetable.create(
            university_id=university_id,
            start_time=start_time,
            end_time=end_time,
        )
