CREATE TABLE pins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gpio INTEGER NOT NULL,
    name VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    password VARCHAR(255),
    role VARCHAR(10),
    status VARCHAR(10),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);




CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pin_number INTEGER,
    pin_name VARCHAR(255),
    name VARCHAR(255),
    user_name VARCHAR(255),
    role VARCHAR(10),
    action VARCHAR(10),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


>>> from app import db
>>> from app import app
>>>
>>>
>>> app.app_context().push()
>>> db.create_all()