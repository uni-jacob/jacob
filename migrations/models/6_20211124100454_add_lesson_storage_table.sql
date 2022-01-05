-- upgrade --
CREATE TABLE IF NOT EXISTS "lesson_storage" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "classroom_id" INT NOT NULL REFERENCES "classrooms" ("id") ON DELETE CASCADE,
    "lesson_type_id" INT NOT NULL REFERENCES "lessontypes" ("id") ON DELETE CASCADE,
    "subject_id" INT NOT NULL REFERENCES "subjects" ("id") ON DELETE CASCADE,
    "teacher_id" INT NOT NULL REFERENCES "teachers" ("id") ON DELETE CASCADE,
    "time_id" INT NOT NULL REFERENCES "timetable" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "week_id" INT NOT NULL REFERENCES "weeks" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "lesson_storage"."id" IS 'Lessons'' Storage ID';
COMMENT ON COLUMN "lesson_storage"."classroom_id" IS 'Classrooms ID';
COMMENT ON COLUMN "lesson_storage"."lesson_type_id" IS 'Lesson types ID';
COMMENT ON COLUMN "lesson_storage"."subject_id" IS 'Course ID';
COMMENT ON COLUMN "lesson_storage"."teacher_id" IS 'Teachers ID';
COMMENT ON COLUMN "lesson_storage"."time_id" IS 'Time ID';
COMMENT ON COLUMN "lesson_storage"."week_id" IS 'Weeks ID';
COMMENT ON TABLE "lesson_storage" IS 'Temporary storage of lessons';
-- downgrade --
DROP TABLE IF EXISTS "lesson_storage";
