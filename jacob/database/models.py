"""Модели базы данных."""

import os
from datetime import datetime
from typing import Iterable, Optional

from pony import orm

from jacob.services.db import get_db_credentials

db = orm.Database()


class AcademicStatus(db.Entity):
    """Формы обучения студентов."""

    description: str = orm.Optional(str, unique=True)
    students: Iterable["Student"] = orm.Set("Student")


class AdminConfig(db.Entity):
    """Хранилище конфигов админов."""

    owner: "Student" = orm.Required("Student")
    names_usage: Optional[bool] = orm.Optional(bool, default=True)
    active_group: Optional["Group"] = orm.Optional("Group")
    active_chat: Optional["Chat"] = orm.Optional("Chat")


class AlmaMater(db.Entity):
    """Университеты."""

    name: str = orm.Required(str)
    groups: Iterable["Group"] = orm.Set("Group")


class Group(db.Entity):
    """Студенческие группы."""

    group_num: str = orm.Required(str)
    specialty: str = orm.Required(str)
    alma_mater: AlmaMater = orm.Required(AlmaMater)
    private: bool = orm.Required(bool)
    admin_configs: Iterable[AdminConfig] = orm.Set(AdminConfig)
    chats: Iterable["Chat"] = orm.Set("Chat")
    admins: Iterable["Admin"] = orm.Set("Admin")
    students: Iterable["Student"] = orm.Set("Student")
    financial_categories: Iterable["FinancialCategory"] = orm.Set("FinancialCategory")
    lists: Iterable["List"] = orm.Set("List")


class Chat(db.Entity):
    """Зарегистрированные чаты."""

    vk_id: int = orm.Required(int)
    group: Group = orm.Required(Group)
    admin_configs: Iterable[AdminConfig] = orm.Set(AdminConfig)


class Admin(db.Entity):
    """Админы бота."""

    student: "Student" = orm.Required("Student")
    group: Group = orm.Required(Group)

    def get_groups(self) -> Iterable[Group]:
        """Возвращает объекты групп, администратором которых является пользователь.

        Returns:
            Iterable[Group]: Объекты групп
        """
        return self.groups


class Student(db.Entity):
    """Студенты."""

    vk_id: int = orm.Required(int)
    first_name: str = orm.Required(str)
    last_name: str = orm.Required(str)
    group: Group = orm.Required(Group)
    subgroup: Optional[int] = orm.Optional(int)
    email: Optional[str] = orm.Optional(str)
    phone_number: Optional[str] = orm.Optional(str)
    academic_status: AcademicStatus = orm.Required(AcademicStatus)
    financial_incomes: Iterable["FinancialIncome"] = orm.Set(
        "FinancialIncome",
        cascade_delete=True,
    )
    issues: Iterable["Issue"] = orm.Set(
        "Issue",
        cascade_delete=True,
    )
    admins: Iterable["Admin"] = orm.Set(
        Admin,
        cascade_delete=True,
    )
    state_storage: Optional["StateStorage"] = orm.Optional(
        "StateStorage",
        cascade_delete=True,
    )
    admin_config: Optional[AdminConfig] = orm.Optional(
        AdminConfig,
        cascade_delete=True,
    )
    call_storage: Optional["MentionStorage"] = orm.Optional(
        "MentionStorage",
        cascade_delete=True,
    )
    chat_registrar_config: Optional["ChatRegistrarConfig"] = orm.Optional(
        "ChatRegistrarConfig",
        cascade_delete=True,
    )
    financial_config: Optional["FinancialConfig"] = orm.Optional(
        "FinancialConfig",
        cascade_delete=True,
    )
    liststudents: Iterable["ListStudents"] = orm.Set(
        "ListStudents",
        cascade_delete=True,
    )

    def is_admin(self) -> bool:
        """
        Проверяет, является ли студент администратором.

        Returns:
            bool: статус администрирования студента
        """
        return not self.admins.is_empty()


class MentionStorage(db.Entity):
    """Хранилище призыва."""

    owner: Student = orm.Required(Student)
    mention_text: Optional[str] = orm.Optional(str)
    mentioned_students: Optional[str] = orm.Optional(str)
    mention_attaches: Optional[str] = orm.Optional(str)


class ChatRegistrarConfig(db.Entity):
    """Хранилище регистратора чатов."""

    owner: Student = orm.Required(Student)
    phrase: Optional[str] = orm.Optional(str, default="")


class FinancialCategory(db.Entity):
    """Финансовые категории."""

    name: Optional[str] = orm.Optional(str)
    summ: Optional[int] = orm.Optional(int)
    group: Group = orm.Required(Group)
    financial_configs: Iterable["FinancialConfig"] = orm.Set("FinancialConfig")
    financial_incomes: Iterable["FinancialIncome"] = orm.Set("FinancialIncome")
    financial_expenses: Iterable["FinancialExpense"] = orm.Set("FinancialExpense")


class FinancialConfig(db.Entity):
    """Временное хранилище активной финансовой категории."""

    owner: Student = orm.Required(Student)
    financial_category: Optional[FinancialCategory] = orm.Optional(FinancialCategory)


class FinancialIncome(db.Entity):
    """Доходы."""

    financial_category: FinancialCategory = orm.Required(FinancialCategory)
    student: Student = orm.Required(Student)
    summ: int = orm.Required(int)
    create_date: datetime = orm.Required(datetime, default=lambda: datetime.now())
    update_date: Optional[datetime] = orm.Optional(datetime)


class FinancialExpense(db.Entity):
    """Расходы."""

    financial_category: FinancialCategory = orm.Required(FinancialCategory)
    summ: int = orm.Required(int)
    create_date: Optional[datetime] = orm.Optional(
        datetime,
        default=lambda: datetime.now(),
    )


class Issue(db.Entity):
    """Баги."""

    owner: Student = orm.Required(Student)
    title: Optional[str] = orm.Optional(str)
    text: Optional[str] = orm.Optional(str)


class State(db.Entity):
    """Статусы боты."""

    description: Optional[str] = orm.Optional(str, unique=True)
    state_storages: Iterable["StateStorage"] = orm.Set("StateStorage")


class StateStorage(db.Entity):
    """Связка состояний ботов с пользователями."""

    owner: Student = orm.Required(Student)
    state: State = orm.Required(State, default=1)


class List(db.Entity):
    """Кастомные списки студентов."""

    group: Group = orm.Required(Group)
    name: str = orm.Required(str)
    students: Iterable["ListStudents"] = orm.Set("ListStudents")


class ListStudents(db.Entity):
    """Связка списков и студентов."""

    list: List = orm.Required(List)
    student: Student = orm.Required(Student)


db.bind(provider="postgres", **get_db_credentials(os.getenv("DATABASE_URL")))
db.generate_mapping(create_tables=True)
