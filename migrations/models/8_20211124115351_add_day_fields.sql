-- upgrade --
ALTER TABLE "lessons" ADD "day_id" INT NOT NULL;
ALTER TABLE "lesson_storage" ADD "day_id" INT;
ALTER TABLE "lessons" ADD CONSTRAINT "fk_lessons_daysofwe_8ace1db2" FOREIGN KEY ("day_id") REFERENCES "daysofweek" ("id") ON DELETE CASCADE;
ALTER TABLE "lesson_storage" ADD CONSTRAINT "fk_lesson_s_daysofwe_5c56f7de" FOREIGN KEY ("day_id") REFERENCES "daysofweek" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "lesson_storage" DROP CONSTRAINT "fk_lesson_s_daysofwe_5c56f7de";
ALTER TABLE "lessons" DROP CONSTRAINT "fk_lessons_daysofwe_8ace1db2";
ALTER TABLE "lessons" DROP COLUMN "day_id";
ALTER TABLE "lesson_storage" DROP COLUMN "day_id";
