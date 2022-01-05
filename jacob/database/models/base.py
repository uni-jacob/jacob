import re

from tortoise import fields
from tortoise.models import Model
from tortoise.validators import RegexValidator


class Personality(Model):
    id: int = fields.IntField(pk=True, description="ID")
    first_name: str = fields.CharField(
        max_length=255,
        null=False,
        description="Name",
    )
    last_name: str = fields.CharField(
        max_length=255,
        null=False,
        description="Last name",
    )


class User(Model):
    """Анонимный пользователь."""

    id: int = fields.IntField(pk=True, description="Users ID 2")
    vk_id: int = fields.IntField(
        null=False,
        unique=True,
        description="Users VK ID",
    )

    class Meta:
        table = "users"
        table_description = "User"


class Student(Personality):
    """Зарегистрированный студент."""

    user: int = fields.ForeignKeyField("models.User", description="Users ID 3")
    group: "Group" = fields.ForeignKeyField(
        "models.Group",
        description="Users group",
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
        table_description = "Registered student"


class Group(Model):
    """Студенческая группа."""

    id: int = fields.IntField(
        pk=True,
        description="Groups ID",
    )
    group_number: str = fields.CharField(
        max_length=20,
        description="Groups name",
    )
    specialty: str = fields.CharField(
        max_length=255,
        description="Specialties name",
    )
    university: "University" = fields.ForeignKeyField(
        "models.University",
        description="Groups university",
    )

    class Meta:
        table = "groups"
        table_description = "Group"


class University(Model):
    """Университет."""

    id: int = fields.IntField(
        pk=True,
        description="Universities ID",
    )
    name: str = fields.CharField(
        max_length=255,
        null=False,
        description="Universities name",
    )
    abbreviation: str = fields.CharField(
        max_length=13,
        null=True,
        description="Universities abbreviation",
    )

    class Meta:
        table = "universities"
        table_description = "University"


class State(Model):
    id: int = fields.IntField(
        pk=True,
        description="States ID",
    )
    description: str = fields.CharField(
        max_length=255,
        null=False,
        description="States description",
    )

    class Meta:
        table = "states"
        table_description = "State"


class StateStorage(Model):
    id: int = fields.IntField(
        pk=True,
        description="States storages ID",
    )
    user: "User" = fields.ForeignKeyField(
        "models.User",
        "Users ID 2",
    )
    state: "State" = fields.ForeignKeyField(
        "models.State",
        "States ID",
        default=1,
    )

    class Meta:
        table = "statestorage"
        table_description = "States storage"


class Admin(Model):
    id: int = fields.IntField(
        pk=True,
        description="Admins ID",
    )
    user: "User" = fields.ForeignKeyField(
        "models.User",
        "Users ID",
    )
    group: "Group" = fields.ForeignKeyField(
        "models.Group",
        "Groups ID",
    )
    is_active: bool = fields.BooleanField(default=True)

    class Meta:
        table = "admin"
        table_description = "Admin"
