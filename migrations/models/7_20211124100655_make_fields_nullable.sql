-- upgrade --
ALTER TABLE "lesson_storage" ALTER COLUMN "teacher_id" DROP NOT NULL;
ALTER TABLE "lesson_storage" ALTER COLUMN "time_id" DROP NOT NULL;
ALTER TABLE "lesson_storage" ALTER COLUMN "subject_id" DROP NOT NULL;
ALTER TABLE "lesson_storage" ALTER COLUMN "classroom_id" DROP NOT NULL;
ALTER TABLE "lesson_storage" ALTER COLUMN "lesson_type_id" DROP NOT NULL;
ALTER TABLE "lesson_storage" ALTER COLUMN "week_id" DROP NOT NULL;
-- downgrade --
ALTER TABLE "lesson_storage" ALTER COLUMN "teacher_id" SET NOT NULL;
ALTER TABLE "lesson_storage" ALTER COLUMN "time_id" SET NOT NULL;
ALTER TABLE "lesson_storage" ALTER COLUMN "subject_id" SET NOT NULL;
ALTER TABLE "lesson_storage" ALTER COLUMN "classroom_id" SET NOT NULL;
ALTER TABLE "lesson_storage" ALTER COLUMN "lesson_type_id" SET NOT NULL;
ALTER TABLE "lesson_storage" ALTER COLUMN "week_id" SET NOT NULL;
