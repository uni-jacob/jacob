"""Модели базы данных."""

import os
from datetime import datetime

from pony.orm import Database, Optional, Required, Set

from jacob.services.db import get_db_credentials

db = Database()


class AcademicStatus(db.Entity):
    """Формы обучения студентов."""

    description = Optional(str, unique=True)
    students = Set("Student")


class AdminConfig(db.Entity):
    """Хранилище конфигов админов."""

    admin = Required("Admin")
    names_usage = Optional(bool, default=True)
    active_group = Optional("Group")
    active_chat = Optional("Chat")


class AlmaMater(db.Entity):
    """Университеты."""

    name = Required(str)
    groups = Set("Group")


class Group(db.Entity):
    """Студенческие группы."""

    group_num = Required(str)
    specialty = Required(str)
    alma_mater = Required(AlmaMater)
    admin_configs = Set(AdminConfig)
    chats = Set("Chat")
    admins = Set("Admin")
    students = Set("Student")
    financial_categories = Set("FinancialCategory")


class Chat(db.Entity):
    """Зарегистрированные чаты."""

    vk_id = Required(int)
    group = Required(Group)
    admin_configs = Set(AdminConfig)


class Admin(db.Entity):
    """Админы бота."""

    student = Required("Student")
    groups = Set(Group)
    admin_config = Optional(AdminConfig)
    call_storage = Optional("CallStorage")
    chat_registrar_config = Optional("ChatRegistrarConfig")
    financial_config = Optional("FinancialConfig")
    state_storage = Optional("StateStorage")

    def get_groups(self):
        """Возвращает объекты групп, администратором которых является пользователь.

        Returns:
            Set[Group]: Объекты групп
        """
        return self.groups


class Student(db.Entity):
    """Студенты."""

    vk_id = Required(int)
    first_name = Required(str)
    last_name = Required(str)
    group = Required(Group)
    subgroup = Optional(int)
    email = Optional(str)
    phone_number = Required(int)
    academic_status = Required(AcademicStatus)
    financial_incomes = Set("FinancialIncome")
    issues = Set("Issue")
    admins = Set(Admin)

    def is_admin(self) -> bool:
        """
        Проверяет, является ли студент администратором.

        Returns:
            bool: статус администрирования студента
        """
        return not self.admins.is_empty()


class MentionStorage(db.Entity):
    """Хранилище призыва."""

    admin = Required(Admin)


class ChatRegistrarConfig(db.Entity):
    """Хранилище регистратора чатов."""

    admin = Required(Admin)
    phrase = Optional(str, default="")


class FinancialCategory(db.Entity):
    """Финансовые категории."""

    name = Optional(str)
    summ = Optional(int)
    group = Required(Group)
    financial_configs = Set("FinancialConfig")
    financial_incomes = Set("FinancialIncome")
    financial_expenses = Set("FinancialExpense")


class FinancialConfig(db.Entity):
    """Временное хранилище активной финансовой категории."""

    admin = Required(Admin)
    financial_category = Required(FinancialCategory)


class FinancialIncome(db.Entity):
    """Доходы."""

    financial_category = Required(FinancialCategory)
    student = Required(Student)
    summ = Required(int)
    create_date = Required(datetime, default=lambda: datetime.now())
    update_date = Optional(datetime)


class FinancialExpense(db.Entity):
    """Расходы."""

    financial_category = Required(FinancialCategory)
    summ = Required(int)
    create_date = Optional(datetime, default=lambda: datetime.now())


class Issue(db.Entity):
    """Баги."""

    author = Required(Student)
    title = Required(str)
    text = Optional(str)


class State(db.Entity):
    """Статусы боты."""

    description = Optional(str, unique=True)
    state_storages = Set("StateStorage")


class StateStorage(db.Entity):
    """Связка состояний ботов с администраторами."""

    admin = Required(Admin)
    state = Required(State)


db.bind(provider="postgres", **get_db_credentials(os.getenv("DATABASE_URL")))
db.generate_mapping(create_tables=True)
