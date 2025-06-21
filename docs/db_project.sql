CREATE TABLE IF NOT EXISTS "user" (
	"id" serial NOT NULL,
	"firstname" varchar(50),
	"lastname" varchar(50),
	"email" varchar(50) UNIQUE,
	"tg_id" bigint NOT NULL UNIQUE,
	"is_admin" boolean NOT NULL DEFAULT false,
	"team_id" bigint,
	"register_at" timestamp with time zone NOT NULL,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "team" (
	"id" serial NOT NULL,
	"name" varchar(50) NOT NULL UNIQUE,
	"leader_id" bigint NOT NULL,
	"sector_ids" bigint NOT NULL,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "sector" (
	"id" serial NOT NULL,
	"name" varchar(50) NOT NULL UNIQUE,
	"curator_id" bigint NOT NULL,
	"color" varchar(7) NOT NULL DEFAULT '#000000',
	"geometry" geometry NOT NULL UNIQUE,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "tree" (
	"id" serial NOT NULL,
	"planting" varchar(50),
	"species" varchar(50),
	"description" varchar(255),
	"condition" varchar(255) NOT NULL,
	"location" geometry NOT NULL,
	"sector_id" bigint NOT NULL,
	"removed" boolean NOT NULL,
	"emergency" boolean NOT NULL DEFAULT false,
	"author" bigint NOT NULL,
	"created_at" timestamp with time zone NOT NULL,
	"updated_at" timestamp with time zone NOT NULL,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "photo" (
	"id" serial NOT NULL,
	"file_path" varchar(255) NOT NULL,
	"uploaded_at" timestamp with time zone NOT NULL,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "defect_type" (
	"id" serial NOT NULL,
	"name" varchar(50) NOT NULL UNIQUE,
	"description" varchar(255),
	"images" bigint NOT NULL,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "survey_defect" (
	"id" serial NOT NULL,
	"defect_status" varchar(255) NOT NULL,
	"defect_id" bigint NOT NULL,
	"description" varchar(255),
	"survey_defect_photo" bigint NOT NULL,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "survey" (
	"id" serial NOT NULL UNIQUE,
	"tree_id" bigint NOT NULL,
	"age" bigint,
	"height" varchar(255),
	"diameter" varchar(255),
	"trunk_count" bigint NOT NULL DEFAULT '1',
	"survey_status" bigint,
	"condition" bigint,
	"defect_ids" bigint NOT NULL,
	"author" bigint NOT NULL,
	"created_at" timestamp with time zone NOT NULL,
	"updated_at" timestamp with time zone NOT NULL,
	"tree_photo" bigint NOT NULL,
	PRIMARY KEY ("id")
);

ALTER TABLE "user" ADD CONSTRAINT "user_fk6" FOREIGN KEY ("team_id") REFERENCES "team"("id");
ALTER TABLE "team" ADD CONSTRAINT "team_fk2" FOREIGN KEY ("leader_id") REFERENCES "user"("id");

ALTER TABLE "team" ADD CONSTRAINT "team_fk3" FOREIGN KEY ("sector_ids") REFERENCES "sector"("id");
ALTER TABLE "sector" ADD CONSTRAINT "sector_fk2" FOREIGN KEY ("curator_id") REFERENCES "user"("id");
ALTER TABLE "tree" ADD CONSTRAINT "tree_fk6" FOREIGN KEY ("sector_id") REFERENCES "sector"("id");

ALTER TABLE "tree" ADD CONSTRAINT "tree_fk9" FOREIGN KEY ("author") REFERENCES "user"("id");

ALTER TABLE "defect_type" ADD CONSTRAINT "defect_type_fk3" FOREIGN KEY ("images") REFERENCES "photo"("id");
ALTER TABLE "survey_defect" ADD CONSTRAINT "survey_defect_fk2" FOREIGN KEY ("defect_id") REFERENCES "defect_type"("id");

ALTER TABLE "survey_defect" ADD CONSTRAINT "survey_defect_fk4" FOREIGN KEY ("survey_defect_photo") REFERENCES "photo"("id");
ALTER TABLE "survey" ADD CONSTRAINT "survey_fk1" FOREIGN KEY ("tree_id") REFERENCES "tree"("id");

ALTER TABLE "survey" ADD CONSTRAINT "survey_fk8" FOREIGN KEY ("defect_ids") REFERENCES "survey_defect"("id");

ALTER TABLE "survey" ADD CONSTRAINT "survey_fk9" FOREIGN KEY ("author") REFERENCES "user"("id");

ALTER TABLE "survey" ADD CONSTRAINT "survey_fk12" FOREIGN KEY ("tree_photo") REFERENCES "photo"("id");