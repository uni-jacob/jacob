from tortoise.transactions import in_transaction

from jacob.database import models


async def create_group(
    group_number: str, specialty: str, university_id: int
) -> models.Group:
    """
    Создаёт новую группу

    Args:
        group_number: Номер группы
        specialty: Название специальности
        university_id: ИД университета

    Returns:
        Group: Объект созданной группы
    """
    async with in_transaction():
        return await models.Group.create(**locals())
