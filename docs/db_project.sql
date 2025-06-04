-- === Группы пользователей ===
CREATE TABLE IF NOT EXISTS "group" (
	"id" serial PRIMARY KEY,
	"name" varchar(50) NOT NULL UNIQUE
);

-- === Пользователи ===
CREATE TABLE IF NOT EXISTS "user" (
	"id" serial PRIMARY KEY,
	"name" varchar(50),
	"surname" varchar(50),
	"tg_id" bigint NOT NULL UNIQUE,
	"email" varchar(50) UNIQUE,
	"is_admin" boolean NOT NULL DEFAULT false,
	"is_leader" boolean NOT NULL DEFAULT false,
	"group" bigint NOT NULL REFERENCES "group"("id"),
	"register_at" date NOT NULL
);

-- === Секторы ===
CREATE TABLE IF NOT EXISTS "sector" (
	"id" serial PRIMARY KEY,
	"name" varchar(50) NOT NULL UNIQUE,
	"curator" bigint NOT NULL REFERENCES "user"("id"),
	"color" varchar(7) NOT NULL DEFAULT '#000000'
);

-- === Связь сектор-группа (многие-ко-многим) ===
CREATE TABLE IF NOT EXISTS "sector_group" (
	"id" serial PRIMARY KEY,
	"sector" bigint NOT NULL REFERENCES "sector"("id"),
	"group" bigint NOT NULL REFERENCES "group"("id")
);

-- === Справочник состояний дерева ===
CREATE TABLE IF NOT EXISTS "tree_condition" (
	"id" serial PRIMARY KEY,
	"name" varchar(50) NOT NULL UNIQUE
);

-- === Справочник статусов тикета ===
CREATE TABLE IF NOT EXISTS "ticket_status" (
	"id" serial PRIMARY KEY,
	"name" varchar(50) NOT NULL UNIQUE
);

-- === Основная таблица тикетов (деревья) ===
CREATE TABLE IF NOT EXISTS "ticket" (
	"id" serial PRIMARY KEY,
	"planting" varchar(50),
	"breed" varchar(50),
	"description" varchar(255),
	"age" bigint,
	"height" bigint,
	"diameter" bigint,
	"trunk_count" bigint NOT NULL DEFAULT 1,
	"condition_id" bigint NOT NULL REFERENCES "tree_condition"("id"),
	"long" double precision NOT NULL,
	"lat" double precision NOT NULL,
	"azimuth" bigint,
	"dist" bigint,
	"sector" bigint NOT NULL REFERENCES "sector"("id"),
	"emergency" boolean NOT NULL DEFAULT false,
	"author" bigint NOT NULL REFERENCES "user"("id"),
	"status_id" bigint NOT NULL REFERENCES "ticket_status"("id"),
	"created_at" date NOT NULL,
	"updated_at" date NOT NULL
);

-- === Справочник повреждений ===
CREATE TABLE IF NOT EXISTS "damage" (
	"id" serial PRIMARY KEY,
	"name" varchar(50) NOT NULL UNIQUE,
	"description" varchar(255)
);

-- === Связь тикета и повреждения (многие-ко-многим) ===
CREATE TABLE IF NOT EXISTS "ticket_damage" (
	"id" serial PRIMARY KEY,
	"status" bigint NOT NULL,
	"ticket" bigint NOT NULL REFERENCES "ticket"("id"),
	"damage" bigint NOT NULL REFERENCES "damage"("id")
);

-- === Фото повреждений (привязка к ticket_damage) ===
CREATE TABLE IF NOT EXISTS "photo" (
	"id" serial PRIMARY KEY,
	"ticket_damage" bigint NOT NULL REFERENCES "ticket_damage"("id"),
	"image" bytea NOT NULL UNIQUE,
	"lat" double precision,
	"long" double precision
	-- Дополнительно можно: filename, mimetype, created_at
);

-- === Галерея обучающих изображений ===
CREATE TABLE IF NOT EXISTS "training_gallery" (
	"id" serial PRIMARY KEY,
	"trauma" bigint NOT NULL REFERENCES "damage"("id"),
	"photo" bytea NOT NULL UNIQUE
);

-- === Контрольные точки по секторам ===
CREATE TABLE IF NOT EXISTS "point" (
	"id" serial PRIMARY KEY,
	"lat" double precision NOT NULL,
	"long" double precision NOT NULL,
	"sector" bigint NOT NULL REFERENCES "sector"("id")
);



CREATE INDEX idx_ticket_sector ON ticket(sector);
CREATE INDEX idx_ticket_author ON ticket(author);
CREATE INDEX idx_ticket_status ON ticket(status_id);
CREATE INDEX idx_ticket_condition ON ticket(condition_id);
CREATE INDEX idx_ticket_damage_ticket ON ticket_damage(ticket);
CREATE INDEX idx_ticket_damage_damage ON ticket_damage(damage);
CREATE INDEX idx_photo_ticket_damage ON photo(ticket_damage);
