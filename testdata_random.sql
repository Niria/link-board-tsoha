BEGIN;

DO $$
DECLARE 
parent INTEGER;
loremlong TEXT = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras tempus fermentum sem, quis accumsan eros. Sed iaculis posuere tortor sed rhoncus. Mauris semper egestas euismod. Nam non pulvinar metus. Aliquam non massa nulla. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Sed ultrices efficitur diam, non tristique tortor lobortis eget. Integer et porttitor turpis. Nam rhoncus sodales ipsum ut feugiat. Curabitur rhoncus semper orci et consequat. Morbi ultricies, tellus quis efficitur luctus, magna nulla faucibus enim, vel dictum tellus massa et mi. Suspendisse at ante purus. ';
loremshort TEXT = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras tempus fermentum sem, quis accumsan eros. Sed iaculis posuere tortor sed rhoncus. Mauris semper egestas euismod. Nam non pulvinar metus. Aliquam non massa nulla. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.';
example_url TEXT = 'https://www.example.com';
t threads%rowtype;
reply replies%rowtype;
news_id INTEGER;
science_id INTEGER;
nature_id INTEGER;
sports_id INTEGER;
programming_id INTEGER;
politics_id INTEGER;


BEGIN

-- Create 6 categories
INSERT INTO categories (name, is_public) VALUES ('News', 'true') RETURNING id INTO news_id;
INSERT INTO categories (name, is_public) VALUES ('Science', 'true') RETURNING id INTO science_id;
INSERT INTO categories (name, is_public) VALUES ('Nature', 'true') RETURNING id INTO nature_id;
INSERT INTO categories (name, is_public) VALUES ('Sports', 'true') RETURNING id INTO sports_id;
INSERT INTO categories (name, is_public) VALUES ('Programming', 'true') RETURNING id INTO programming_id;
INSERT INTO categories (name, is_public) VALUES ('Politics', 'false') RETURNING id INTO politics_id;


-- Create 5 static test users
INSERT INTO users (username, display_name, password, user_role) 
VALUES ('user1', 'User 1', 'scrypt:32768:8:1$gGcL4tROHg2ObV9m$aa0a5a3a79050279924dcb8eb4dc5b926bc36acea513b33a4e8bbd54a375ad6b6e205fa5db8b1c8c0615468de5b9eff91bc2098afa643308bf130f9bf367892c', 1);
INSERT INTO users (username, display_name, password, user_role) 
VALUES ('user2', 'User 2', 'scrypt:32768:8:1$gGcL4tROHg2ObV9m$aa0a5a3a79050279924dcb8eb4dc5b926bc36acea513b33a4e8bbd54a375ad6b6e205fa5db8b1c8c0615468de5b9eff91bc2098afa643308bf130f9bf367892c', 0);
INSERT INTO users (username, display_name, password, user_role) 
VALUES ('user3', 'User 3', 'scrypt:32768:8:1$gGcL4tROHg2ObV9m$aa0a5a3a79050279924dcb8eb4dc5b926bc36acea513b33a4e8bbd54a375ad6b6e205fa5db8b1c8c0615468de5b9eff91bc2098afa643308bf130f9bf367892c', 0);
INSERT INTO users (username, display_name, password, user_role) 
VALUES ('user4', 'User 4', 'scrypt:32768:8:1$gGcL4tROHg2ObV9m$aa0a5a3a79050279924dcb8eb4dc5b926bc36acea513b33a4e8bbd54a375ad6b6e205fa5db8b1c8c0615468de5b9eff91bc2098afa643308bf130f9bf367892c', 0);
INSERT INTO users (username, display_name, password, user_role) 
VALUES ('user5', 'User 5', 'scrypt:32768:8:1$gGcL4tROHg2ObV9m$aa0a5a3a79050279924dcb8eb4dc5b926bc36acea513b33a4e8bbd54a375ad6b6e205fa5db8b1c8c0615468de5b9eff91bc2098afa643308bf130f9bf367892c', 0);

-- Generate 100 dummy users
INSERT INTO users (username, display_name, password, user_role, created_at)
SELECT 'dummy_user_' || i::varchar(8), 'DummyUser-' || i::varchar(8), md5(random()::text), 0, now() - random() * interval '21 days'
FROM generate_series(1,100) AS i;

-- Generate dummy threads 
WITH thread AS (
    SELECT (SELECT id FROM categories WHERE ts IS NOT NULL ORDER BY random() LIMIT 1) AS category_id,
    (SELECT id FROM users WHERE created_at < ts ORDER BY random() LIMIT 1) AS user_id,
    ts AS created_at
    FROM generate_series(now() - interval '14 days', now() - interval '10 minutes', interval '2 hours' + random() * interval '4 hour') AS t(ts)
)
INSERT INTO threads (category_id, title, content, link_url, user_id, created_at)
SELECT category_id, 
       (SELECT initcap(name) FROM categories WHERE id=category_id) || ' dummy link #' || row_number() over(), 
       loremlong, 
       example_url, 
       user_id, 
       created_at 
FROM thread;

-- Loop through threads adding dummy replies and then add a random amount of thread likes
FOR t IN SELECT * FROM threads
LOOP
    FOR i IN 1..floor(random()*50::int)
    LOOP
        SELECT * FROM replies WHERE thread_id=t.id ORDER BY random() LIMIT 1 INTO reply;

        INSERT INTO replies (user_id, thread_id, parent_id, content, created_at)
        SELECT (SELECT users.id FROM users WHERE users.created_at < t.created_at ORDER BY random() LIMIT 1),
            t.id,
            (SELECT (array[reply.id, null])[floor(random()* 2 + 1)]),
            loremshort,
            COALESCE(reply.created_at + random() * least(interval '2 days', now() - reply.created_at), 
                        t.created_at + random() * least(interval '2 days', now() - t.created_at));
    END LOOP;

    INSERT INTO thread_likes (user_id, thread_id)
    SELECT id, t.id
    FROM users TABLESAMPLE BERNOULLI(floor(random()*50)) WHERE id > 5;
END LOOP;

-- Loop through dummy replies and add a random amount of likes
FOR reply IN SELECT * FROM replies
LOOP
    INSERT INTO reply_likes (user_id, reply_id)
    SELECT id, reply.id
    FROM users TABLESAMPLE BERNOULLI(floor(random()*30)) WHERE id > 5;
END LOOP;

END $$;
COMMIT;
