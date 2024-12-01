BEGIN;

DO $$
DECLARE 
parent INTEGER;
loremlong TEXT = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras tempus fermentum sem, quis accumsan eros. Sed iaculis posuere tortor sed rhoncus. Mauris semper egestas euismod. Nam non pulvinar metus. Aliquam non massa nulla. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Sed ultrices efficitur diam, non tristique tortor lobortis eget. Integer et porttitor turpis. Nam rhoncus sodales ipsum ut feugiat. Curabitur rhoncus semper orci et consequat. Morbi ultricies, tellus quis efficitur luctus, magna nulla faucibus enim, vel dictum tellus massa et mi. Suspendisse at ante purus. ';
loremshort TEXT = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras tempus fermentum sem, quis accumsan eros. Sed iaculis posuere tortor sed rhoncus. Mauris semper egestas euismod. Nam non pulvinar metus. Aliquam non massa nulla. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.';
example_url TEXT = 'https://www.example.com';
u users%rowtype;
t threads%rowtype;
--u users%rowtype;
par_reply replies%rowtype;
reply replies%rowtype;
news_id INTEGER;
science_id INTEGER;
nature_id INTEGER;
sports_id INTEGER;
programming_id INTEGER;
politics_id INTEGER;


BEGIN

-- Create categories
INSERT INTO categories (name, is_public) VALUES ('News', 'true') RETURNING id INTO news_id;
INSERT INTO categories (name, is_public) VALUES ('Science', 'true') RETURNING id INTO science_id;
INSERT INTO categories (name, is_public) VALUES ('Nature', 'true') RETURNING id INTO nature_id;
INSERT INTO categories (name, is_public) VALUES ('Sports', 'true') RETURNING id INTO sports_id;
INSERT INTO categories (name, is_public) VALUES ('Programming', 'true') RETURNING id INTO programming_id;
INSERT INTO categories (name, is_public) VALUES ('Politics', 'false') RETURNING id INTO politics_id;


-- Create users
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

-- Create threads
INSERT INTO threads (category_id, title, content, link_url, user_id) 
VALUES (1, 'Test news article 1', loremshort, 'https://www.example.com', 1);
INSERT INTO threads (category_id, title, content, link_url, user_id) 
VALUES (2, 'Test science article 1', loremshort, 'https://www.example.com', 2);
INSERT INTO threads (category_id, title, content, link_url, user_id) 
VALUES (3, 'Test nature article 1', loremshort, 'https://www.example.com', 3);
INSERT INTO threads (category_id, title, content, link_url, user_id) 
VALUES (4, 'Test sports article 1', loremshort, 'https://www.example.com', 4);
INSERT INTO threads (category_id, title, content, link_url, user_id) 
VALUES (5, 'Test programming article 1', loremshort, 'https://www.example.com', 5);
INSERT INTO threads (category_id, title, content, link_url, user_id) 
VALUES (6, 'Test political article 1', loremshort, 'https://www.example.com', 1);

-- Loop users and create threads
FOR u IN
    SELECT * FROM users
LOOP
    INSERT INTO threads (category_id, title, content, link_url, user_id, created_at) 
    VALUES (news_id, CONCAT('User', u.id, ' news article'), loremshort, 'https://www.example.com', u.id, now() - random() * interval '1 month');
    INSERT INTO threads (category_id, title, content, link_url, user_id, created_at) 
    VALUES (science_id, CONCAT('User', u.id, ' science article'), loremshort, 'https://www.example.com', u.id, now() - random() * interval '1 month');
    INSERT INTO threads (category_id, title, content, link_url, user_id, created_at) 
    VALUES (nature_id, CONCAT('User', u.id, ' nature article'), loremshort, 'https://www.example.com', u.id, now() - random() * interval '1 month');
    INSERT INTO threads (category_id, title, content, link_url, user_id, created_at) 
    VALUES (sports_id, CONCAT('User', u.id, ' sports article'), loremshort, 'https://www.example.com', u.id, now() - random() * interval '1 month');
    INSERT INTO threads (category_id, title, content, link_url, user_id, created_at) 
    VALUES (programming_id, CONCAT('User', u.id, ' programming article'), loremshort, 'https://www.example.com', u.id, now() - random() * interval '1 month');
    INSERT INTO threads (category_id, title, content, link_url, user_id, created_at) 
    VALUES (politics_id, CONCAT('User', u.id, ' political article'), loremshort, 'https://www.example.com', u.id, now() - random() * interval '1 month');
END LOOP;

-- Loop threads and loop users generating replies
FOR t IN 
    SELECT * FROM threads
LOOP
    FOR u IN
        SELECT * FROM users
    LOOP
        INSERT INTO replies (user_id, thread_id, parent_id, content)
        VALUES (u.id, t.id, NULL, loremlong);
        
        INSERT INTO replies (user_id, thread_id, parent_id, content)
        SELECT u.id, t.id, (SELECT id FROM replies WHERE thread_id=t.id ORDER BY random() LIMIT 1), loremlong
        FROM generate_series(1,(floor(random()*5)::int));
    END LOOP;
END LOOP;

END $$;
COMMIT;
