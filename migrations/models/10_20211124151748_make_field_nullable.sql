-- upgrade --
ALTER TABLE "lessons" ALTER COLUMN "group_id" DROP NOT NULL;
-- downgrade --
ALTER TABLE "lessons" ALTER COLUMN "group_id" SET NOT NULL;
