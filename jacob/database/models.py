import re

from tortoise import fields
from tortoise.models import Model
from tortoise.validators import RegexValidator


class User(Model):
    """Анонимный пользователь."""

    id: int = fields.IntField(pk=True, description="ИД пользователя")
    vk_id: int = fields.IntField(
        null=False,
        unique=True,
        description="ИД ВК пользователя",
    )

    class Meta:
        table = "anonymous_users"
        table_description = "Анонимный пользователь"


class Student(User):
    """Зарегистрированный студент."""

    first_name: str = fields.CharField(
        max_length=255,
        null=False,
        description="Имя студента",
    )
    last_name: str = fields.CharField(
        max_length=255,
        null=False,
        description="Фамилия студента",
    )
    group = fields.ForeignKeyField(
        "models.Group",
        description="Группа",
    )
    subgroup = fields.IntField()
    email = fields.CharField(
        max_length=255,
        validators=[
            RegexValidator(
                r"^[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+$",
                re.I,
            ),
        ],
    )
    phone = fields.IntField(
        validators=[
            RegexValidator(
                r"^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$",
                re.I,
            ),
        ],
    )

    class Meta:
        table = "students"
        table_description = "Зарегистрированный студент"


class Group(Model):
    """Студенческая группа."""

    id: int = fields.IntField(
        pk=True,
        description="ИД группы",
    )
    group_number: str = fields.CharField(
        max_length=20,
        description="Номер группы",
    )
    specialty: str = fields.CharField(
        max_length=255,
        description="Название специальности",
    )
    university: int = fields.ForeignKeyField(
        "models.University",
        description="Университет",
    )
    private: bool = fields.BooleanField(
        description="Приватность группы",
    )

    class Meta:
        table = "groups"
        table_description = "Студенческая группа"


class University(Model):
    """Университет."""

    id: int = fields.IntField(
        pk=True,
        description="ИД университета",
    )
    name: str = fields.CharField(
        max_length=255,
        null=False,
        description="Название университета",
    )

    class Meta:
        table = "universities"
        table_description = "Университет"
