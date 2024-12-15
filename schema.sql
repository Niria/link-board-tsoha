BEGIN;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(24) UNIQUE NOT NULL,
    display_name VARCHAR(24) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    profile_public BOOLEAN DEFAULT TRUE,
    description TEXT,
    user_role SMALLINT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(32) UNIQUE NOT NULL,
    description VARCHAR(255),
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

CREATE TABLE threads (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories NOT NULL,
    user_id INTEGER REFERENCES users,
    title VARCHAR(64) NOT NULL,
    content TEXT,
    link_url VARCHAR(64) NOT NULL,
    thumbnail BYTEA,
    visible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

CREATE TABLE replies (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users NOT NULL,
    thread_id INTEGER REFERENCES threads NOT NULL,
    parent_id INTEGER REFERENCES replies,
    content TEXT NOT NULL,
    visible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

CREATE TABLE thread_likes (
    thread_id INTEGER REFERENCES threads NOT NULL,
    user_id INTEGER REFERENCES users NOT NULL,
    PRIMARY KEY (thread_id, user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reply_likes (
    reply_id INTEGER REFERENCES replies NOT NULL,
    user_id INTEGER REFERENCES users NOT NULL,
    PRIMARY KEY (reply_id, user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE permissions (
    category_id INTEGER REFERENCES categories NOT NULL,
    user_id INTEGER REFERENCES users NOT NULL,
    PRIMARY KEY (category_id, user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_followers (
    user_id INTEGER REFERENCES users NOT NULL,
    follower_id INTEGER REFERENCES users NOT NULL,
    PRIMARY KEY (user_id, follower_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE category_favourites (
    user_id INTEGER REFERENCES  users NOT NULL,
    category_id INTEGER REFERENCES categories NOT NULL,
    PRIMARY KEY (user_id, category_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX users_username ON users (username);
CREATE INDEX categories_name ON categories (name);
CREATE INDEX threads_title ON threads (title);
CREATE INDEX threads_category_id ON threads (category_id);
CREATE INDEX threads_user_id ON threads (user_id);
CREATE INDEX replies_user_id ON replies (user_id);
CREATE INDEX replies_thread_id ON replies (thread_id);
CREATE INDEX replies_parent_id ON replies (parent_id);
CREATE INDEX thread_likes_user_id ON thread_likes (user_id);
CREATE INDEX reply_likes_user_id ON reply_likes (user_id);
CREATE INDEX permissions_user_id ON permissions (user_id);
CREATE INDEX user_followers_follower_id ON user_followers (follower_id);
CREATE INDEX category_favourites_category_id ON category_favourites (category_id);

CREATE OR REPLACE FUNCTION time_ago (since TIMESTAMP WITH TIME ZONE)
RETURNS TEXT
LANGUAGE plpgsql
AS
$$
DECLARE
  ago TEXT;
BEGIN

WITH t(diff) AS (
  select CURRENT_TIMESTAMP - since
)
SELECT COALESCE(NULLIF(EXTRACT(day FROM diff), 0)||' day',
                NULLIF(EXTRACT(hour FROM diff), 0)||' hour',
                NULLIF(EXTRACT(minute FROM diff), 0)||' minute',
                'just now')
INTO ago
FROM t;

CASE WHEN ago ~ '^([2-9]|\d{2,})\s.*' THEN SELECT ago || 's ago' INTO ago;
     WHEN ago ~ '^1\s.*' THEN SELECT ago || ' ago' INTO ago;
     ELSE
END CASE;

RETURN ago;
END;
$$;

CREATE OR REPLACE FUNCTION edit_date() RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        NEW.updated_at := NULL;
    ELSIF TG_OP = 'UPDATE' THEN
        NEW.updated_at := now();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER user_edit_date
    BEFORE INSERT OR UPDATE
    ON users
    FOR EACH ROW
    EXECUTE PROCEDURE edit_date();

CREATE TRIGGER category_edit_date
    BEFORE INSERT OR UPDATE
    ON categories
    FOR EACH ROW
    EXECUTE PROCEDURE edit_date();

CREATE TRIGGER thread_edit_date
    BEFORE INSERT OR UPDATE
    ON threads
    FOR EACH ROW
    EXECUTE PROCEDURE edit_date();

CREATE TRIGGER reply_edit_date
    BEFORE INSERT OR UPDATE
    ON replies
    FOR EACH ROW
    EXECUTE PROCEDURE edit_date();

COMMIT;