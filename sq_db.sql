CREATE TABLE IF NOT EXISTS user(
id integer PRIMARY KEY AUTOINCREMENT,
login text NOT NULL,
password text NOT NULL
);
--CREATE TABLE IF NOT EXISTS type(
--id integer PRIMARY KEY AUTOINCREMENT,
--name text NOT NULL,
--);
CREATE TABLE IF NOT EXISTS link(
id integer PRIMARY KEY AUTOINCREMENT,
link text NOT NULL,
psev text NOT NULL,
type text NOT NULL,
count integer NOT NULL,
id_user integer NOT NULL FOREIGN KEY('id_user') REFERENCES "users" ("id")
);