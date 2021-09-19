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
        table = "users"
        table_description = "Пользователь"


class Student(Model):
    """Зарегистрированный студент."""

    id: int = fields.IntField(pk=True, description="ИД студента")
    user: int = fields.ForeignKeyField("models.User", description="ИД пользователя")
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
    group: "Group" = fields.ForeignKeyField(
        "models.Group",
        description="Группа",
    )
    subgroup = fields.IntField(
        null=True,
    )
    email = fields.CharField(
        max_length=255,
        validators=[
            RegexValidator(
                r"^[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+$",
                re.I,
            ),
        ],
        null=True,
    )
    phone = fields.IntField(
        validators=[
            RegexValidator(
                r"^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$",
                re.I,
            ),
        ],
        null=True,
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
    university: "University" = fields.ForeignKeyField(
        "models.University",
        description="Университет",
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
    abbreviation: str = fields.CharField(
        max_length=13,
        null=True,
        description="Сокращенное название университета",
    )

    class Meta:
        table = "universities"
        table_description = "Университет"


class State(Model):
    id: int = fields.IntField(
        pk=True,
        description="ИД стейта",
    )
    description: str = fields.CharField(
        max_length=255,
        null=False,
        description="Описание стейта",
    )

    class Meta:
        table = "states"
        table_description = "Стейт"


class StateStorage(Model):
    id: int = fields.IntField(
        pk=True,
        description="ИД хранилища стейтов",
    )
    user: "User" = fields.ForeignKeyField(
        "models.User",
        "ИД пользователя",
    )
    state: "State" = fields.ForeignKeyField(
        "models.State",
        "ИД стейта",
        default=1,
    )

    class Meta:
        table = "statestorage"
        table_description = "Хранилище стейтов"


class Admin(Model):
    id: int = fields.IntField(
        pk=True,
        description="ИД админа",
    )
    user: "User" = fields.ForeignKeyField(
        "models.User",
        "ИД пользователя 2",
    )
    group: "Group" = fields.ForeignKeyField(
        "models.Group",
        "ИД группы",
    )
    is_active: bool = fields.BooleanField(default=True)

    class Meta:
        table = "admin"
        table_description = "Админ"
