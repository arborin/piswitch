CREATE TABLE pins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gpio INTEGER NOT NULL,
    name VARCHAR(255)
);