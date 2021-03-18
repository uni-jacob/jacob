"""Генерация тестовых данных для базы данных."""


from mimesis import Person
from mimesis import Text
from mimesis.random import Random
from pony import orm

from jacob.database import models


@orm.db_session
def generate_ac_statuses() -> list:
    ac_statuses_objects = []
    ac_statuses = [
        "Бюджетная основа",
        "Контрактная основа",
        "Целевой договор",
        "Иностранцы",
        "Отчислен",
    ]
    for name in ac_statuses:
        ac_statuses_objects.append(models.AcademicStatus(description=name))
    return ac_statuses_objects


@orm.db_session
def generate_universities() -> list:
    person = Person("ru")
    universities = []
    universities_objects = []
    for _ in range(5):
        university = person.university()
        universities.append(university)
        universities_objects.append(models.AlmaMater(name=university))
    return universities_objects


@orm.db_session
def generate_groups() -> list:
    groups_objects = []
    for _ in range(5):
        group_num = Random().custom_code("@@@-###")
        specialty = " ".join(Text("ru").words(quantity=2))
        alma_mater = orm.select(am for am in models.AlmaMater).random(1)[0]
        groups_objects.append(
            models.Group(
                group_num=group_num,
                specialty=specialty,
                alma_mater=alma_mater,
            ),
        )
    return groups_objects


@orm.db_session
def generate_bot_statuses() -> list:
    bot_statuses_objects = []
    bot_statuses = [
        "main",
        "fin_select_donater",
        "fin_enter_donate_sum",
        "fin_confirm_debtors_call",
        "mention_wait_text",
        "mention_confirm",
        "fin_enter_expense_sum",
        "pref_confirm_chat_register",
        "common_select_chat",
        "report_wait_title",
        "report_wait_text",
        "contacts_select_student",
        "mention_select_mentioned",
        "fin_wait_category_desc",
        "send_alert_fin_started",
    ]
    for name in bot_statuses:
        bot_statuses_objects.append(models.State(description=name))
    return bot_statuses_objects


person = Person("ru")

with orm.db_session:
    if not orm.select(am for am in models.AlmaMater)[:]:
        print("Генерация универов")
        unies = generate_universities()
    if not orm.select(gr for gr in models.Group)[:]:
        print("Генерация групп")
        groups = generate_groups()
    else:
        print("Селектинг групп")
        groups = orm.select(gr for gr in models.Group)[:]
    if orm.select(acs for acs in models.AcademicStatus)[:]:
        print("Селектинг форм обучения")
        ac_statuses = orm.select(acs for acs in models.AcademicStatus)[:]
    else:
        print("Генерация форм обучения")
        ac_statuses = generate_ac_statuses()
    if orm.select(st for st in models.State)[:]:
        print("Селектинг статусов")
        bot_statuses = orm.select(st for st in models.State)[:]
    else:
        print("Генерация статусов")
        bot_statuses = generate_bot_statuses()

for i in range(20):
    vk_id = Random().custom_code(mask="#########")
    name, surname = person.full_name().split()
    email = person.email()
    phone = person.telephone(mask="9#########")
    with orm.db_session:
        ac_status = orm.select(ac for ac in models.AcademicStatus).random(1)[0]
        group = orm.select(gr for gr in models.Group).random(1)[0]
        st = models.Student(
            vk_id=vk_id,
            first_name=name,
            last_name=surname,
            email=email,
            phone_number=phone,
            group=group,
            academic_status=ac_status,
        )
with orm.db_session:
    me = models.Student(
        vk_id=549350532,
        first_name="Даниил",
        last_name="Голубев",
        group=1,
        academic_status=1,
    )
    models.Admin(student=me, group=me.group)
    for group in orm.select(gr for gr in models.Group):
        random_student = orm.select(
            st for st in models.Student if st.group == group
        ).random(1)[0]
        models.Admin(
            student=random_student,
            group=group,
        )
