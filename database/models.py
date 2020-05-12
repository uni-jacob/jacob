from tortoise.models import Model
from tortoise import fields


class AcademicStatus(Model):
    id = fields.IntField(pk=True)
    description = fields.CharField(max_length=50)

    class Meta:
        table = "academic_statuses"


class Administrator(Model):
    id = fields.IntField(pk=True)
    vk_id = fields.ForeignKeyField("models.Student", to_field="vk_id")
    alma_mater_id = fields.ForeignKeyField("models.AlmaMater")
    group_id = fields.ForeignKeyField("models.Group")

    class Meta:
        table = "administrators"


class AlmaMater(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=300)

    class Meta:
        table = "alma_maters"


class CachedChat(Model):
    id = fields.IntField(pk=True)
    chat_id = fields.BigIntField()

    class Meta:
        table = "cached_chats"


class CallStorage(Model):
    id = fields.IntField(pk=True)
    selected_students = fields.TextField()
    call_text = fields.TextField()
    call_attaches = fields.TextField()

    class Meta:
        table = "call_storage"


class Chat(Model):
    id = fields.IntField(pk=True)
    chat_id = fields.BigIntField()
    alma_mater_id = fields.ForeignKeyField("models.AlmaMater")
    group_id = fields.ForeignKeyField("models.Group")
    chat_type = fields.IntField()

    class Meta:
        table = "chats"


class FinancialCategory(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=35)
    summ = fields.IntField()
    alma_mater_id = fields.ForeignKeyField("models.AlmaMater")
    group_id = fields.ForeignKeyField("models.Group")

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
    alma_mater_id = fields.IntField()

    class Meta:
        table = "groups"


class MailingStorage(Model):
    id = fields.IntField(pk=True)
    mailing_id = fields.IntField()
    mailing_text = fields.TextField()
    mailing_attaches = fields.TextField()

    class Meta:
        table = "mailing_storage"


class Mailing(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=30)
    alma_mater_id = fields.ForeignKeyField("models.AlmaMater")
    group_id = fields.ForeignKeyField("models.Group")

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


class Student(Model):
    id = fields.IntField(pk=True)
    vk_id = fields.BigIntField(unique=True)
    first_name = fields.CharField(max_length=50)
    second_name = fields.CharField(max_length=50)
    alma_mater = fields.ForeignKeyField("models.AlmaMater")
    fields.ForeignKeyField("models.Group")
    academic_status = fields.IntField()

    class Meta:
        table = "students"


class Subscription(Model):
    student_id = fields.IntField()
    mailing_id = fields.IntField()
    status = fields.BooleanField()

    class Meta:
        table = "subscriptions"
