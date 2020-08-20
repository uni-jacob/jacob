from peewee import AutoField
from peewee import BigIntegerField
from peewee import BooleanField
from peewee import CharField
from peewee import Check
from peewee import ForeignKeyField
from peewee import IntegerField
from peewee import Model
from peewee import PostgresqlDatabase
from peewee import TextField
from peewee import TimestampField
from peewee import fn

from services.db import get_db_credentials

db = PostgresqlDatabase(**get_db_credentials())


class BaseModel(Model):
    class Meta:
        database = db

    def __str__(self):
        return f"<{type(self).__name__}: {self._pk}>"


class AcademicStatus(BaseModel):
    id = AutoField(primary_key=True,)
    description = CharField()

    class Meta:
        table_name = "academic_statuses"


class AlmaMater(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField()

    class Meta:
        table_name = "alma_maters"


class Group(BaseModel):
    id = AutoField(primary_key=True,)
    group_num = CharField()
    specialty = TextField()
    alma_mater = ForeignKeyField(
        AlmaMater, backref="almamater", on_delete="CASCADE", on_update="CASCADE"
    )

    class Meta:
        table_name = "groups"


class Administrator(BaseModel):
    id = IntegerField(primary_key=True)
    group_id = ForeignKeyField(
        Group, backref="groups", on_delete="CASCADE", on_update="CASCADE"
    )

    class Meta:
        table_name = "administrators"


class CachedChat(BaseModel):
    id = AutoField(primary_key=True)
    chat_id = IntegerField(unique=True)

    class Meta:
        table_name = "cached_chats"


class ChatType(BaseModel):
    id = AutoField(primary_key=True,)
    description = CharField(unique=True)

    class Meta:
        table_name = "chat_types"


class Chat(BaseModel):
    id = AutoField(primary_key=True,)
    chat_id = BigIntegerField(unique=True)
    group_id = ForeignKeyField(
        Group, backref="groups", on_delete="CASCADE", on_update="CASCADE"
    )
    chat_type = ForeignKeyField(ChatType, backref="chattypes", on_delete="RESTRICT")

    class Meta:
        table_name = "chats"


class FinancialCategory(BaseModel):
    id = AutoField(primary_key=True,)
    name = CharField()
    summ = IntegerField()
    group_id = ForeignKeyField(
        Group, backref="groups", on_delete="CASCADE", on_update="CASCADE"
    )

    class Meta:
        table_name = "financial_categories"


class Student(BaseModel):
    id = AutoField(primary_key=True,)
    vk_id = BigIntegerField(unique=True, constraints=[Check("vk_id > 0")])
    first_name = CharField()
    second_name = CharField()
    group_id = ForeignKeyField(
        Group, backref="groups", on_delete="CASCADE", on_update="CASCADE"
    )
    academic_status = ForeignKeyField(
        AcademicStatus,
        backref="academicstatuses",
        default=1,
        on_delete="RESTRICT",
        on_update="CASCADE",
    )

    class Meta:
        table_name = "students"


class FinancialDonate(BaseModel):
    id = AutoField(primary_key=True,)
    category = ForeignKeyField(
        FinancialCategory,
        backref="categories",
        on_delete="CASCADE",
        on_update="CASCADE",
    )
    student = ForeignKeyField(
        Student, backref="students", on_delete="CASCADE", on_update="CASCADE"
    )
    summ = IntegerField()
    create_date = TimestampField(default=fn.NOW())
    update_date = TimestampField()

    class Meta:
        table_name = "financial_donates"


class FinancialExpences(BaseModel):
    id = AutoField(primary_key=True,)
    category = ForeignKeyField(
        FinancialCategory,
        backref="categories",
        on_delete="CASCADE",
        on_update="CASCADE",
    )
    summ = IntegerField()
    create_date = TimestampField(default=fn.NOW())

    class Meta:
        table_name = "financial_expences"


class State(BaseModel):
    id = AutoField(primary_key=True,)
    description = CharField()

    class Meta:
        table_name = "states"


class Storage(BaseModel):
    id = AutoField(primary_key=True,)
    state_id = ForeignKeyField(
        State, backref="states", default=1, on_delete="SET DEFAULT", on_update="CASCADE"
    )
    current_chat = ForeignKeyField(
        ChatType,
        backref="chattypes",
        default=0,
        on_delete="SET DEFAULT",
        on_update="CASCADE",
    )
    names_usage = BooleanField(default=False)
    selected_students = TextField(default="")
    text = TextField(default="")
    attaches = TextField(default="")

    class Meta:
        table_name = "storages"
