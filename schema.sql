DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS certificates;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

CREATE TABLE certificates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    year TEXT NOT NULL,
    category TEXT NOT NULL,
    sport TEXT NOT NULL,
    event TEXT NOT NULL,
    filename TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
