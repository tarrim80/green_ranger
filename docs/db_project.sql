CREATE TABLE IF NOT EXISTS "user" (
	"id" serial NOT NULL,
	"name" varchar(50),
	"surname" varchar(50),
	"tg_id" bigint NOT NULL UNIQUE,
	"email" varchar(50) UNIQUE,
	"is_admin" boolean NOT NULL DEFAULT false,
	"register_at" timestamp with time zone NOT NULL,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "team" (
	"id" serial NOT NULL,
	"name" varchar(50) NOT NULL UNIQUE,
	"leader_id" bigint NOT NULL,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "sector" (
	"id" serial NOT NULL,
	"name" varchar(50) NOT NULL UNIQUE,
	"curator_id" bigint NOT NULL,
	"color" varchar(7) NOT NULL DEFAULT '#000000',
	"geometry" geometry NOT NULL UNIQUE,
	"team_id" bigint NOT NULL,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "ticket" (
	"id" serial NOT NULL,
	"planting" varchar(50),
	"species" varchar(50),
	"description" varchar(255),
	"age" bigint,
	"height" varchar(255),
	"diameter" varchar(255),
	"trunk_count" bigint NOT NULL DEFAULT '1',
	"condition" varchar(255) NOT NULL,
	"location" geometry NOT NULL,
	"azimuth" varchar(255),
	"dist" varchar(255),
	"sector_id" bigint NOT NULL,
	"curator_id" bigint NOT NULL,
	"ticket_status" varchar(255) NOT NULL,
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

CREATE TABLE IF NOT EXISTS "damage" (
	"id" serial NOT NULL,
	"name" varchar(50) NOT NULL UNIQUE,
	"description" varchar(255),
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "ticket_damage" (
	"id" serial NOT NULL,
	"damage_status" varchar(255) NOT NULL,
	"ticket_id" bigint NOT NULL,
	"damage_id" bigint NOT NULL,
	"description" varchar(255),
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "ticket_photo" (
	"id" serial NOT NULL UNIQUE,
	"ticket_id" bigint NOT NULL,
	"photo_id" bigint NOT NULL,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "ticket_damage_photo" (
	"id" serial NOT NULL UNIQUE,
	"ticket_damage_id" bigint NOT NULL,
	"photo_id" bigint NOT NULL,
	PRIMARY KEY ("id")
);


ALTER TABLE "team" ADD CONSTRAINT "team_fk2" FOREIGN KEY ("leader_id") REFERENCES "user"("id");
ALTER TABLE "sector" ADD CONSTRAINT "sector_fk2" FOREIGN KEY ("curator_id") REFERENCES "user"("id");

ALTER TABLE "sector" ADD CONSTRAINT "sector_fk5" FOREIGN KEY ("team_id") REFERENCES "team"("id");
ALTER TABLE "ticket" ADD CONSTRAINT "ticket_fk12" FOREIGN KEY ("sector_id") REFERENCES "sector"("id");

ALTER TABLE "ticket" ADD CONSTRAINT "ticket_fk13" FOREIGN KEY ("curator_id") REFERENCES "user"("id");

ALTER TABLE "ticket" ADD CONSTRAINT "ticket_fk16" FOREIGN KEY ("author") REFERENCES "user"("id");


ALTER TABLE "ticket_damage" ADD CONSTRAINT "ticket_damage_fk2" FOREIGN KEY ("ticket_id") REFERENCES "ticket"("id");

ALTER TABLE "ticket_damage" ADD CONSTRAINT "ticket_damage_fk3" FOREIGN KEY ("damage_id") REFERENCES "damage"("id");
ALTER TABLE "ticket_photo" ADD CONSTRAINT "ticket_photo_fk1" FOREIGN KEY ("ticket_id") REFERENCES "ticket"("id");

ALTER TABLE "ticket_photo" ADD CONSTRAINT "ticket_photo_fk2" FOREIGN KEY ("photo_id") REFERENCES "photo"("id");
ALTER TABLE "ticket_damage_photo" ADD CONSTRAINT "ticket_damage_photo_fk1" FOREIGN KEY ("ticket_damage_id") REFERENCES "ticket_damage"("id");

ALTER TABLE "ticket_damage_photo" ADD CONSTRAINT "ticket_damage_photo_fk2" FOREIGN KEY ("photo_id") REFERENCES "photo"("id");