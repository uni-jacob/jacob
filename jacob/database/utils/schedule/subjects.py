from typing import Optional

from tortoise.transactions import in_transaction

from jacob.database import models


async def get_subjects(group_id: int) -> list[models.Subject]:
    async with in_transaction():
        return await models.Subject.filter(group_id=group_id)


async def find_subject(**kwargs) -> Optional[models.Subject]:
    async with in_transaction():
        return await models.Subject.get_or_none(**kwargs)


async def create_subject(group: models.Group, full_name: str) -> models.Subject:
    async with in_transaction():
        return await models.Subject.create(group=group, full_name=full_name)


async def update_subject(subject_id: int, **kwargs) -> models.Subject:
    async with in_transaction():
        query = await models.Subject(id=subject_id).update_from_dict(kwargs)
        await query.save()
        return await models.Subject.get(id=subject_id)
