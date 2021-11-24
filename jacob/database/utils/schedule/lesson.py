from typing import Optional

from tortoise.transactions import in_transaction

from jacob.database import models
from jacob.database.utils.students import get_student


async def create_lesson_from_storage(
    storage: models.LessonTempStorage,
) -> models.Lesson:
    async with in_transaction():
        student = await get_student(user_id=storage.user.id)
        group = await student.group
        return await models.Lesson.create(
            lesson_type_id=storage.lesson_type.id,
            week_id=storage.week.id,
            day_id=storage.day.id,
            time_id=storage.time.id,
            subject_id=storage.subject.id,
            teacher_id=storage.teacher.id,
            classroom_id=storage.classroom.id,
            group_id=group.id,
        )


async def find_lesson(
    week: int,
    day: int,
    time: int,
    group: int,
) -> Optional[models.Lesson]:
    async with in_transaction():
        return (
            await models.Lesson.filter(
                week_id=week,
                day_id=day,
                time_id=time,
                group_id=group,
            )
            .prefetch_related(
                "week",
                "day",
                "time",
                "subject",
                "teacher",
                "classroom",
                "lesson_type",
            )
            .first()
        )
