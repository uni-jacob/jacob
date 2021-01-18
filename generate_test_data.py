import random

from mimesis import Person
from mimesis import Text
from mimesis.random import Random
from pony import orm

from jacob.database import models


@orm.db_session
def generate_ac_statuses():
    ac_statuses = []
    for name in [
        "Бюджетная основа",
        "Контрактная основа",
        "Целевой договор",
        "Иностранцы",
        "Отчислен",
    ]:
        ac_statuses.append(models.AcademicStatus(description=name))
    return ac_statuses


@orm.db_session
def generate_universities():
    p = Person("ru")
    universities = []
    universities_objects = []
    for i in range(5):
        university = p.university()
        universities.append(university)
        universities_objects.append(models.AlmaMater(name=university))
    return universities_objects


@orm.db_session
def generate_groups():
    groups_objects = []
    for _ in range(5):
        group_num = Random().custom_code("@@@-###")
        specialty = " ".join(Text("ru").words(quantity=2))
        alma_mater = random.choice(orm.select(am for am in models.AlmaMater)[:])
        groups_objects.append(
            models.Group(
                group_num=group_num, specialty=specialty, alma_mater=alma_mater
            )
        )
    return groups_objects


@orm.db_session
def generate_bot_statuses():
    bot_statuses = []
    for name in [
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
        "common_select_student",
        "common_select_mentioned",
        "fin_wait_category_desc",
    ]:
        bot_statuses.append(models.State(description=name))
    return bot_statuses


p = Person("ru")

with orm.db_session:
    if not orm.select(am for am in models.AlmaMater)[:]:
        unies = generate_universities()
    if not orm.select(gr for gr in models.Group)[:]:
        groups = generate_groups()
    else:
        groups = orm.select(gr for gr in models.Group)[:]
    if not orm.select(acs for acs in models.AcademicStatus)[:]:
        ac_statuses = generate_ac_statuses()
    else:
        ac_statuses = orm.select(acs for acs in models.AcademicStatus)[:]
    if not orm.select(st for st in models.State)[:]:
        bot_statuses = generate_bot_statuses()
    else:
        bot_statuses = orm.select(st for st in models.State)[:]

for i in range(20):
    vk_id = Random().custom_code(mask="#########")
    name, surname = p.full_name().split()
    email = p.email()
    phone = p.telephone(mask="9#########")
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
    for group in orm.select(gr for gr in models.Group):
        models.Admin(
            student=orm.select(st for st in models.Student if st.group == group).random(
                1
            )[0],
        )
