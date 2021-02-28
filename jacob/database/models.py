"""Модели базы данных."""

import os
from datetime import datetime

from pony import orm

from jacob.services.db import get_db_credentials

db = orm.Database()


class AcademicStatus(db.Entity):
    """Формы обучения студентов."""

    description = orm.Optional(str, unique=True)
    students = orm.Set("Student")


class AdminConfig(db.Entity):
    """Хранилище конфигов админов."""

    owner = orm.Required("Student")
    names_usage = orm.Optional(bool, default=True)
    active_group = orm.Optional("Group")
    active_chat = orm.Optional("Chat")


class AlmaMater(db.Entity):
    """Университеты."""

    name = orm.Required(str)
    groups = orm.Set("Group")


class Group(db.Entity):
    """Студенческие группы."""

    group_num = orm.Required(str)
    specialty = orm.Required(str)
    alma_mater = orm.Required(AlmaMater)
    admin_configs = orm.Set(AdminConfig)
    chats = orm.Set("Chat")
    admins = orm.Set("Admin")
    students = orm.Set("Student")
    financial_categories = orm.Set("FinancialCategory")


class Chat(db.Entity):
    """Зарегистрированные чаты."""

    vk_id = orm.Required(int)
    group = orm.Required(Group)
    admin_configs = orm.Set(AdminConfig)


class Admin(db.Entity):
    """Админы бота."""

    student = orm.Required("Student")
    group = orm.Required(Group)

    def get_groups(self):
        """Возвращает объекты групп, администратором которых является пользователь.

        Returns:
            orm.Set[Group]: Объекты групп
        """
        return self.groups


class Student(db.Entity):
    """Студенты."""

    vk_id = orm.Required(int)
    first_name = orm.Required(str)
    last_name = orm.Required(str)
    group = orm.Required(Group)
    subgroup = orm.Optional(int)
    email = orm.Optional(str)
    phone_number = orm.Optional(str)
    academic_status = orm.Required(AcademicStatus)
    financial_incomes = orm.Set("FinancialIncome")
    issues = orm.Set("Issue")
    admins = orm.Set(Admin)
    state_storage = orm.Optional("StateStorage")
    admin_config = orm.Optional(AdminConfig)
    call_storage = orm.Optional("MentionStorage")
    chat_registrar_config = orm.Optional("ChatRegistrarConfig")
    financial_config = orm.Optional("FinancialConfig")

    def is_admin(self) -> bool:
        """
        Проверяет, является ли студент администратором.

        Returns:
            bool: статус администрирования студента
        """
        return not self.admins.is_empty()


class MentionStorage(db.Entity):
    """Хранилище призыва."""

    owner = orm.Required(Student)
    mention_text = orm.Optional(str)
    mentioned_students = orm.Optional(str)
    mention_attaches = orm.Optional(str)


class ChatRegistrarConfig(db.Entity):
    """Хранилище регистратора чатов."""

    owner = orm.Required(Student)
    phrase = orm.Optional(str, default="")


class FinancialCategory(db.Entity):
    """Финансовые категории."""

    name = orm.Optional(str)
    summ = orm.Optional(int)
    group = orm.Required(Group)
    financial_configs = orm.Set("FinancialConfig")
    financial_incomes = orm.Set("FinancialIncome")
    financial_expenses = orm.Set("FinancialExpense")


class FinancialConfig(db.Entity):
    """Временное хранилище активной финансовой категории."""

    owner = orm.Required(Student)
    financial_category = orm.Required(FinancialCategory)


class FinancialIncome(db.Entity):
    """Доходы."""

    financial_category = orm.Required(FinancialCategory)
    student = orm.Required(Student)
    summ = orm.Required(int)
    create_date = orm.Required(datetime, default=lambda: datetime.now())
    update_date = orm.Optional(datetime)


class FinancialExpense(db.Entity):
    """Расходы."""

    financial_category = orm.Required(FinancialCategory)
    summ = orm.Required(int)
    create_date = orm.Optional(datetime, default=lambda: datetime.now())


class Issue(db.Entity):
    """Баги."""

    author = orm.Required(Student)
    title = orm.Required(str)
    text = orm.Optional(str)


class State(db.Entity):
    """Статусы боты."""

    description = orm.Optional(str, unique=True)
    state_storages = orm.Set("StateStorage")


class StateStorage(db.Entity):
    """Связка состояний ботов с пользователями."""

    owner = orm.Required(Student)
    state = orm.Required(State, default=1)


db.bind(provider="postgres", **get_db_credentials(os.getenv("DATABASE_URL")))
db.generate_mapping(create_tables=True)
