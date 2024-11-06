BEGIN;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    display_name TEXT,
    password TEXT NOT NULL,
    profile_public BOOLEAN DEFAULT TRUE,
    user_role SMALLINT DEFAULT 0
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    is_public BOOLEAN DEFAULT FALSE
);

CREATE TABLE threads (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories,
    title TEXT NOT NULL,
    content TEXT,
    link_url TEXT NOT NULL,
    visible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE replies (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users NOT NULL,
    thread_id INTEGER REFERENCES threads NOT NULL,
    parent_id INTEGER REFERENCES replies,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE permissions (
    user_id INTEGER REFERENCES users NOT NULL,
    category_id INTEGER REFERENCES categories NOT NULL,
    PRIMARY KEY (user_id, category_id),
    can_read BOOLEAN DEFAULT TRUE,
    can_write BOOLEAN DEFAULT TRUE
);

COMMIT;