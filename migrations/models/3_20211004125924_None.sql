-- upgrade --
CREATE TABLE IF NOT EXISTS "daysofweek" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(11) NOT NULL,
    "abbreviation" VARCHAR(2) NOT NULL
);
COMMENT ON COLUMN "daysofweek"."id" IS 'Day of weeks ID';
COMMENT ON COLUMN "daysofweek"."name" IS 'Day of weeks name';
COMMENT ON COLUMN "daysofweek"."abbreviation" IS 'Abbreviation';
COMMENT ON TABLE "daysofweek" IS 'Days of week';
CREATE TABLE IF NOT EXISTS "lessontypes" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(30) NOT NULL,
    "abbreviation" VARCHAR(5) NOT NULL
);
COMMENT ON COLUMN "lessontypes"."id" IS 'Lesson types ID';
COMMENT ON COLUMN "lessontypes"."name" IS 'Lesson types name';
COMMENT ON COLUMN "lessontypes"."abbreviation" IS 'Abbreviation';
COMMENT ON TABLE "lessontypes" IS 'Lessons types';
CREATE TABLE IF NOT EXISTS "personality" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "first_name" VARCHAR(255) NOT NULL,
    "last_name" VARCHAR(255) NOT NULL
);
COMMENT ON COLUMN "personality"."id" IS 'ID';
COMMENT ON COLUMN "personality"."first_name" IS 'Name';
COMMENT ON COLUMN "personality"."last_name" IS 'Last name';
CREATE TABLE IF NOT EXISTS "states" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "description" VARCHAR(255) NOT NULL
);
COMMENT ON COLUMN "states"."id" IS 'States ID';
COMMENT ON COLUMN "states"."description" IS 'States description';
COMMENT ON TABLE "states" IS 'State';
CREATE TABLE IF NOT EXISTS "universities" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "abbreviation" VARCHAR(13)
);
COMMENT ON COLUMN "universities"."id" IS 'Universities ID';
COMMENT ON COLUMN "universities"."name" IS 'Universities name';
COMMENT ON COLUMN "universities"."abbreviation" IS 'Universities abbreviation';
COMMENT ON TABLE "universities" IS 'University';
CREATE TABLE IF NOT EXISTS "classrooms" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "building" INT NOT NULL,
    "class_name" VARCHAR(10) NOT NULL,
    "university_id" INT NOT NULL REFERENCES "universities" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "classrooms"."id" IS 'Classrooms ID';
COMMENT ON COLUMN "classrooms"."building" IS 'Buildings number';
COMMENT ON COLUMN "classrooms"."class_name" IS 'Classrooms number';
COMMENT ON COLUMN "classrooms"."university_id" IS 'University';
COMMENT ON TABLE "classrooms" IS 'Classrooms';
CREATE TABLE IF NOT EXISTS "groups" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "group_number" VARCHAR(20) NOT NULL,
    "specialty" VARCHAR(255) NOT NULL,
    "university_id" INT NOT NULL REFERENCES "universities" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "groups"."id" IS 'Groups ID';
COMMENT ON COLUMN "groups"."group_number" IS 'Groups name';
COMMENT ON COLUMN "groups"."specialty" IS 'Specialties name';
COMMENT ON COLUMN "groups"."university_id" IS 'Groups university';
COMMENT ON TABLE "groups" IS 'Group';
CREATE TABLE IF NOT EXISTS "subjects" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "full_name" VARCHAR(255) NOT NULL,
    "abbreviation" VARCHAR(15) NOT NULL,
    "group_id" INT NOT NULL REFERENCES "groups" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "subjects"."id" IS 'Subjects ID';
COMMENT ON COLUMN "subjects"."full_name" IS 'Subjects name';
COMMENT ON COLUMN "subjects"."abbreviation" IS 'Subjects abbreviation';
COMMENT ON COLUMN "subjects"."group_id" IS 'Groups';
COMMENT ON TABLE "subjects" IS 'Subjects';
CREATE TABLE IF NOT EXISTS "teachers" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "first_name" VARCHAR(255) NOT NULL,
    "last_name" VARCHAR(255) NOT NULL,
    "patronymic" VARCHAR(30) NOT NULL,
    "university_id" INT NOT NULL REFERENCES "universities" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "teachers"."id" IS 'ID';
COMMENT ON COLUMN "teachers"."first_name" IS 'Name';
COMMENT ON COLUMN "teachers"."last_name" IS 'Last name';
COMMENT ON COLUMN "teachers"."patronymic" IS 'Teachers patronymic';
COMMENT ON COLUMN "teachers"."university_id" IS 'University';
COMMENT ON TABLE "teachers" IS 'Teachers';
CREATE TABLE IF NOT EXISTS "timetable" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "start_time" VARCHAR(5) NOT NULL,
    "end_time" VARCHAR(5) NOT NULL,
    "university_id" INT NOT NULL REFERENCES "universities" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "timetable"."id" IS 'Time ID';
COMMENT ON COLUMN "timetable"."university_id" IS 'University';
CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "vk_id" INT NOT NULL UNIQUE
);
COMMENT ON COLUMN "users"."id" IS 'Users ID 2';
COMMENT ON COLUMN "users"."vk_id" IS 'Users VK ID';
COMMENT ON TABLE "users" IS 'User';
CREATE TABLE IF NOT EXISTS "admin" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "group_id" INT NOT NULL REFERENCES "groups" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "admin"."id" IS 'Admins ID';
COMMENT ON TABLE "admin" IS 'Admin';
CREATE TABLE IF NOT EXISTS "statestorage" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "state_id" INT NOT NULL  DEFAULT 1 REFERENCES "states" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "statestorage"."id" IS 'States storages ID';
COMMENT ON TABLE "statestorage" IS 'States storage';
CREATE TABLE IF NOT EXISTS "students" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "first_name" VARCHAR(255) NOT NULL,
    "last_name" VARCHAR(255) NOT NULL,
    "email" VARCHAR(255),
    "phone" INT,
    "group_id" INT NOT NULL REFERENCES "groups" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "students"."id" IS 'ID';
COMMENT ON COLUMN "students"."first_name" IS 'Name';
COMMENT ON COLUMN "students"."last_name" IS 'Last name';
COMMENT ON COLUMN "students"."group_id" IS 'Users group';
COMMENT ON COLUMN "students"."user_id" IS 'Users ID 3';
COMMENT ON TABLE "students" IS 'Registered student';
CREATE TABLE IF NOT EXISTS "weeks" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(11) NOT NULL,
    "abbreviation" VARCHAR(1) NOT NULL
);
COMMENT ON COLUMN "weeks"."id" IS 'Weeks ID';
COMMENT ON COLUMN "weeks"."name" IS 'Weeks name';
COMMENT ON COLUMN "weeks"."abbreviation" IS 'Week names abbreviation';
COMMENT ON TABLE "weeks" IS 'Weeks';
CREATE TABLE IF NOT EXISTS "lessons" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "classroom_id" INT NOT NULL REFERENCES "classrooms" ("id") ON DELETE CASCADE,
    "lesson_type_id" INT NOT NULL REFERENCES "lessontypes" ("id") ON DELETE CASCADE,
    "subject_id" INT NOT NULL REFERENCES "subjects" ("id") ON DELETE CASCADE,
    "teacher_id" INT NOT NULL REFERENCES "teachers" ("id") ON DELETE CASCADE,
    "time_id" INT NOT NULL REFERENCES "timetable" ("id") ON DELETE CASCADE,
    "week_id" INT NOT NULL REFERENCES "weeks" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "lessons"."id" IS 'Lessons ID';
COMMENT ON COLUMN "lessons"."classroom_id" IS 'Classrooms ID';
COMMENT ON COLUMN "lessons"."lesson_type_id" IS 'Lesson types ID';
COMMENT ON COLUMN "lessons"."subject_id" IS 'Course ID';
COMMENT ON COLUMN "lessons"."teacher_id" IS 'Teachers ID';
COMMENT ON COLUMN "lessons"."time_id" IS 'Time ID';
COMMENT ON COLUMN "lessons"."week_id" IS 'Weeks ID';
COMMENT ON TABLE "lessons" IS 'Lessons';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSONB NOT NULL
);
