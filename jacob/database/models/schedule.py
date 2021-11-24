from tortoise import fields
from tortoise.models import Model

from jacob.database.models import Group, Personality, University, User


class DayOfWeek(Model):
    id: int = fields.IntField(pk=True, description="Day of weeks ID")
    name: str = fields.CharField(max_length=11, description="Day of weeks name")
    abbreviation: str = fields.CharField(max_length=2, description="Abbreviation")

    class Meta:
        table = "daysofweek"
        table_description = "Days of week"


class Week(Model):
    id: int = fields.IntField(pk=True, description="Weeks ID")
    name: str = fields.CharField(max_length=11, description="Weeks name")
    abbreviation: str = fields.CharField(
        max_length=1,
        description="Week names abbreviation",
    )

    class Meta:
        table = "weeks"
        table_description = "Weeks"


class LessonType(Model):
    id: int = fields.IntField(pk=True, description="Lesson types ID")
    name: str = fields.CharField(max_length=30, description="Lesson types name")
    abbreviation: str = fields.CharField(max_length=5, description="Abbreviation")

    class Meta:
        table = "lessontypes"
        table_description = "Lessons types"


class Teacher(Personality):
    patronymic: str = fields.CharField(
        max_length=30,
        description="Teachers patronymic",
    )
    university: University = fields.ForeignKeyField(
        "models.University",
        description="University",
    )

    class Meta:
        table = "teachers"
        table_description = "Teachers"


class Subject(Model):
    id: int = fields.IntField(pk=True, description="Subjects ID")
    full_name: str = fields.CharField(max_length=255, description="Subjects name")
    abbreviation: str = fields.CharField(
        max_length=15,
        description="Subjects abbreviation",
        null=True,
    )
    group: Group = fields.ForeignKeyField(
        "models.Group",
        description="Groups",
    )

    class Meta:
        table = "subjects"
        table_description = "Subjects"


class Classroom(Model):
    id: int = fields.IntField(pk=True, description="Classrooms ID")
    university: University = fields.ForeignKeyField(
        "models.University",
        description="University",
    )
    building: int = fields.IntField(description="Buildings number")
    class_name: str = fields.CharField(
        max_length=10,
        description="Classrooms number",
        null=True,
    )

    class Meta:
        table = "classrooms"
        table_description = "Classrooms"


class Timetable(Model):
    id: int = fields.IntField(pk=True, description="Time ID")
    university: University = fields.ForeignKeyField(
        "models.University",
        description="University",
    )
    start_time: str = fields.CharField(max_length=5)
    end_time: str = fields.CharField(max_length=5)


class Lesson(Model):
    id: int = fields.IntField(pk=True, description="Lessons ID")
    lesson_type: LessonType = fields.ForeignKeyField(
        "models.LessonType",
        description="Lesson types ID",
    )
    week: Week = fields.ForeignKeyField("models.Week", description="Weeks ID")
    day: DayOfWeek = fields.ForeignKeyField("models.DayOfWeek", description="Day ID")
    time: Timetable = fields.ForeignKeyField("models.Timetable", description="Time ID")
    subject: Subject = fields.ForeignKeyField("models.Subject", description="Course ID")
    teacher: Teacher = fields.ForeignKeyField(
        "models.Teacher",
        description="Teachers ID",
    )
    classroom: Classroom = fields.ForeignKeyField(
        "models.Classroom",
        description="Classrooms ID",
    )
    group: Group = fields.ForeignKeyField(
        "models.Group",
        description="Group ID",
        null=True,
    )

    class Meta:
        table = "lessons"
        table_description = "Lessons"


class LessonTempStorage(Model):
    id: int = fields.IntField(pk=True, description="Lessons' Storage ID")
    user: "User" = fields.ForeignKeyField(
        "models.User",
        "Users ID 3",
    )
    lesson_type: LessonType = fields.ForeignKeyField(
        "models.LessonType",
        description="Lesson types ID",
        null=True,
    )
    week: Week = fields.ForeignKeyField(
        "models.Week",
        description="Weeks ID",
        null=True,
    )
    day: DayOfWeek = fields.ForeignKeyField(
        "models.DayOfWeek",
        description="Day ID",
        null=True,
    )
    time: Timetable = fields.ForeignKeyField(
        "models.Timetable",
        description="Time ID",
        null=True,
    )
    subject: Subject = fields.ForeignKeyField(
        "models.Subject",
        description="Course ID",
        null=True,
    )
    teacher: Teacher = fields.ForeignKeyField(
        "models.Teacher",
        description="Teachers ID",
        null=True,
    )
    classroom: Classroom = fields.ForeignKeyField(
        "models.Classroom",
        description="Classrooms ID",
        null=True,
    )

    class Meta:
        table = "lesson_storage"
        table_description = "Temporary storage of lessons"
