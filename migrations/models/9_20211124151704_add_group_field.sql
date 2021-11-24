-- upgrade --
ALTER TABLE "lessons" ADD "group_id" INT NOT NULL;
ALTER TABLE "lessons" ADD CONSTRAINT "fk_lessons_groups_4213348b" FOREIGN KEY ("group_id") REFERENCES "groups" ("id") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "lessons" DROP CONSTRAINT "fk_lessons_groups_4213348b";
ALTER TABLE "lessons" DROP COLUMN "group_id";
