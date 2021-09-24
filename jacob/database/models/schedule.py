from tortoise import fields
from tortoise.models import Model

from jacob.database.models import Personality, University


class DayOfWeek(Model):
    id: int = fields.IntField(pk=True, description="ИД дня недели")
    name: str = fields.CharField(max_length=11, description="Название дня недели")
    abbreviation: str = fields.CharField(max_length=2, description="Сокращение")

    class Meta:
        table = "daysofweek"
        table_description = "Дни недели"


class Week(Model):
    id: int = fields.IntField(pk=True, description="ИД недели")
    name: str = fields.CharField(max_length=11, description="Название недели")
    abbreviation: str = fields.CharField(
        max_length=1,
        description="Сокращение названия недели",
    )

    class Meta:
        table = "weeks"
        table_description = "Учебные недели"


class LessonType(Model):
    id: int = fields.IntField(pk=True, description="ИД типа занятия")
    name: str = fields.CharField(max_length=30, description="Имя типа занятия")
    abbreviation: str = fields.CharField(max_length=5, description="Сокращение")

    class Meta:
        table = "lessontypes"
        table_description = "Типы занятий"


class Teacher(Personality):
    patronymic: str = fields.CharField(
        max_length=30,
        description="Отчество преподавателя",
    )
    university: University = fields.ForeignKeyField(
        "models.University",
        description="Университет",
    )

    class Meta:
        table = "teachers"
        table_description = "Преподаватели"


class Subject(Model):
    id: int = fields.IntField(pk=True, description="ИД курса")
    full_name: str = fields.CharField(max_length=255, description="Название курса")
    abbreviation: str = fields.CharField(
        max_length=15,
        description="Аббревиатура названия",
    )
    university: University = fields.ForeignKeyField(
        "models.University",
        description="Университет",
    )

    class Meta:
        table = "subjects"
        table_description = "Учебные курсы"


class Classroom(Model):
    id: int = fields.IntField(pk=True, description="ИД аудитории")
    university: University = fields.ForeignKeyField(
        "models.University",
        description="Университет",
    )
    building: int = fields.IntField(description="Учебный корпус")
    class_name: str = fields.CharField(max_length=10, description="Номер аудитории")

    class Meta:
        table = "classrooms"
        table_description = "Аудитории"


class Timetable(Model):
    id: int = fields.IntField(pk=True, description="ИД аудитории")
    university: University = fields.ForeignKeyField(
        "models.University",
        description="Университет",
    )
    start_time: str = fields.CharField(max_length=5)
    end_time: str = fields.CharField(max_length=5)


class Lesson(Model):
    id: int = fields.IntField(pk=True, description="ИД курса")
    lesson_type: LessonType = fields.ForeignKeyField(
        "models.LessonType",
        description="ИД типа занятия",
    )
    week: Week = fields.ForeignKeyField("models.Week", description="ИД недели")
    time: Timetable = fields.ForeignKeyField("models.Timetable", description="ИД пары")
    subject: Subject = fields.ForeignKeyField("models.Subject", description="ИД курса")
    teacher: Teacher = fields.ForeignKeyField(
        "models.Teacher",
        description="ИД преподавателя",
    )
    classroom: Classroom = fields.ForeignKeyField(
        "models.Classroom",
        description="ИД аудитории",
    )

    class Meta:
        table = "lessons"
        table_description = "Пары"
