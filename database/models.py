from tortoise.models import Model
from tortoise import fields


class AcademicStatus(Model):
    id = fields.IntField(pk=True)
    description = fields.CharField(max_length=50, null=False)

    class Meta:
        table = "academic_statuses"


class Administrator(Model):
    id = fields.IntField(pk=True)
    group_id = fields.ForeignKeyField("models.Group", on_delete="CASCADE")

    class Meta:
        table = "administrators"


class AlmaMater(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField(null=False)

    class Meta:
        table = "alma_maters"


class CachedChat(Model):
    id = fields.IntField(pk=True)
    chat_id = fields.BigIntField(null=False, unique=True)

    class Meta:
        table = "cached_chats"


class Chat(Model):
    id = fields.IntField(pk=True)
    chat_id = fields.BigIntField()
    group = fields.ForeignKeyField("models.Group")
    chat_type = fields.ForeignKeyField("models.ChatType", on_delete="RESTRICT")
    active = fields.BooleanField(null=False, default=False)

    class Meta:
        table = "chats"


class FinancialCategory(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=35)
    summ = fields.IntField()
    group_id = fields.ForeignKeyField("models.Group", on_delete="CASCADE")

    class Meta:
        table = "financial_categories"


class FinancialDonate(Model):
    id = fields.IntField(pk=True)
    category_id = fields.IntField()
    student_id = fields.IntField()
    summ = fields.IntField()
    create_date = fields.DatetimeField(auto_now=True)
    update_date = fields.DatetimeField()

    class Meta:
        table = "financial_donates"


class FinancialExpense(Model):
    id = fields.IntField(pk=True)
    category_id = fields.IntField()
    summ = fields.IntField()
    create_date = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "financial_expences"


class Group(Model):
    id = fields.IntField(pk=True)
    group_num = fields.CharField(max_length=20)
    speciality = fields.TextField()
    alma_mater_id = fields.ForeignKeyField("models.AlmaMater", on_delete="RESTRICT")

    class Meta:
        table = "groups"


class Mailing(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=30)
    group_id = fields.ForeignKeyField("models.Group", on_delete="CASCADE")

    class Meta:
        table = "mailings"


class State(Model):
    id = fields.IntField(pk=True)
    description = fields.CharField(max_length=30)

    class Meta:
        table = "states"


class Storage(Model):
    id = fields.IntField(pk=True)
    state_id = fields.IntField()
    current_chat = fields.IntField()
    names_usage = fields.BooleanField()

    class Meta:
        table = "storage"


class CallStorage(Model):
    selected_students = fields.TextField()
    call_text = fields.TextField()
    call_attaches = fields.TextField()
    mailing_id = fields.TextField()

    class Meta:
        table = "call_storage"


class MailingStorage(Model):
    call_text = fields.TextField()
    call_attaches = fields.TextField()
    mailing_id = fields.TextField()

    class Meta:
        table = "mailing_storage"


class Student(Model):
    id = fields.IntField(pk=True)
    vk_id = fields.BigIntField(unique=True)
    first_name = fields.CharField(max_length=50, null=False)
    second_name = fields.CharField(max_length=50, null=False)
    group = fields.ForeignKeyField("models.Group", on_delete="CASCADE")
    academic_status = fields.ForeignKeyField(
        "models.AcademicStatus", on_delete="RESTRICT"
    )

    class Meta:
        table = "students"


class Subscription(Model):
    id = fields.IntField(pk=True)
    student_id = fields.ForeignKeyField('models.Student', on_delete='CASCADE')
    mailing_id = fields.ForeignKeyField('models.Mailing', on_delete='CASCADE')
    status = fields.BooleanField(null=False, default=True)

    class Meta:
        table = "subscriptions"
