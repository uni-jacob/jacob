from tortoise import fields
from tortoise.models import Model


class User(Model):
    """Зарегистрированный пользователь."""

    id: int = fields.IntField(pk=True, description="ИД пользователя")
    vk_id: int = fields.IntField(
        null=False,
        unique=True,
        description="ИД ВК пользователя",
    )
    mode: int = fields.ForeignKeyField(
        "BotMode",
        description="Текущий режим бота у пользователя",
    )
