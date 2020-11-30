import os
from datetime import datetime

from pony.orm import PrimaryKey
from pony.orm import Optional
from pony.orm import Set
from pony.orm import Required
from pony.orm import Database

from jacob.services.db import get_db_credentials

db = Database()


class AcademicStatus(db.Entity):
    id = PrimaryKey(int, auto=True)
    description = Optional(str, 255, unique=True)
    students = Set("Student")


class AdminConfig(db.Entity):
    id = PrimaryKey(int, auto=True)
    names_usage = Optional(bool)
    active_group = Required("Group")
    active_chat = Required("Chat")


class AlmaMater(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    groups = Set("Group")


class Group(db.Entity):
    id = PrimaryKey(int, auto=True)
    group_num = Required(str, 255)
    specialty = Required(str)
    alma_mater = Required(AlmaMater)
    admin_configs = Set(AdminConfig)
    chats = Set("Chat")
    administrators = Set("Administrator")
    students = Set("Student")
    financial_categories = Set("FinancialCategory")


class Chat(db.Entity):
    id = PrimaryKey(int, auto=True)
    vk_id = Required(int)
    group = Required(Group)
    admin_configs = Set(AdminConfig)


class Administrator(db.Entity):
    id = PrimaryKey(int, auto=True)
    student = Required("Student")
    groups = Set(Group)
    call_storage = Optional("CallStorage")
    chat_registrar_config = Optional("ChatRegistrarConfig")
    financial_config = Optional("FinancialConfig")
    state_storage = Optional("StateStorage")


class Student(db.Entity):
    id = PrimaryKey(int, auto=True)
    vk_id = Required(int)
    first_name = Required(str)
    last_name = Required(str)
    group = Required(Group)
    subgroup = Optional(int)
    email = Optional(str, nullable=True)
    phone_number = Required(int)
    academic_status = Required(AcademicStatus)
    financial_incomes = Set("FinancialIncome")
    issues = Set("Issue")
    administrators = Set(Administrator)


class CallStorage(db.Entity):
    id = PrimaryKey(int, auto=True)
    administrator = Required(Administrator)


class ChatRegistrarConfig(db.Entity):
    id = PrimaryKey(int, auto=True)
    administrator = Required(Administrator)
    phrase = Optional(str, default="")


class FinancialCategory(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    summ = Optional(int)
    group = Required(Group)
    financial_configs = Set("FinancialConfig")
    financial_incomes = Set("FinancialIncome")
    financial_expenses = Set("FinancialExpense")


class FinancialConfig(db.Entity):
    id = PrimaryKey(int, auto=True)
    administrator = Required(Administrator)
    financial_category = Required(FinancialCategory)


class FinancialIncome(db.Entity):
    id = PrimaryKey(int, auto=True)
    financial_category = Required(FinancialCategory)
    student = Required(Student)
    summ = Required(int)
    create_date = Required(datetime, default=lambda: datetime.now())
    update_date = Optional(datetime)


class FinancialExpense(db.Entity):
    id = PrimaryKey(int, auto=True)
    financial_category = Required(FinancialCategory)
    summ = Required(int)
    create_date = Optional(datetime, default=lambda: datetime.now())


class Issue(db.Entity):
    id = PrimaryKey(int, auto=True)
    author = Required(Student)
    title = Required(str)
    text = Optional(str, nullable=True)


class State(db.Entity):
    id = PrimaryKey(int, auto=True)
    description = Optional(str, 255, unique=True)
    state_storages = Set("StateStorage")


class StateStorage(db.Entity):
    id = PrimaryKey(int, auto=True)
    administrator = Required(Administrator)
    state = Required(State)


db.bind(provider="postgres", **get_db_credentials(os.getenv("DATABASE_URL")))
db.generate_mapping(create_tables=True)
