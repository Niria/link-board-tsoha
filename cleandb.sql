BEGIN;

DROP TRIGGER IF EXISTS user_edit_date ON users;
DROP TRIGGER IF EXISTS category_edit_date ON categories;
DROP TRIGGER IF EXISTS thread_edit_date ON threads;
DROP TRIGGER IF EXISTS reply_edit_date ON replies;

DROP TABLE IF EXISTS category_favourites;
DROP TABLE IF EXISTS user_followers;
DROP TABLE IF EXISTS thread_likes;
DROP TABLE IF EXISTS reply_likes;
DROP TABLE IF EXISTS replies;
DROP TABLE IF EXISTS threads;
DROP TABLE IF EXISTS permissions;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;
DROP FUNCTION IF EXISTS time_ago(since TIMESTAMP WITH TIME ZONE);
DROP FUNCTION IF EXISTS edit_date();

COMMIT;