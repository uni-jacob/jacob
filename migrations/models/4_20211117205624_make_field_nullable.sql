-- upgrade --
ALTER TABLE "subjects" ALTER COLUMN "abbreviation" DROP NOT NULL;
-- downgrade --
ALTER TABLE "subjects" ALTER COLUMN "abbreviation" SET NOT NULL;
