-- upgrade --
ALTER TABLE "classrooms" ALTER COLUMN "class_name" DROP NOT NULL;
-- downgrade --
ALTER TABLE "classrooms" ALTER COLUMN "class_name" SET NOT NULL;
