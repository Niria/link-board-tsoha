from .db import db
from sqlalchemy.sql import text


def get_category_list(user_id: int = None):
    sql = text("""SELECT c.name
                    FROM categories AS c
                   WHERE (c.is_public=:public 
                      OR (SELECT user_role > 0 
                            FROM users 
                           WHERE id=:user_id)
                      OR c.id IN (SELECT p.category_id 
                                    FROM permissions AS p
                                   WHERE p.user_id=:user_id))
                   ORDER BY c.name""")
    categories = db.session.execute(sql, {"public":True, "user_id":user_id})
    return categories.fetchall()

def get_category(category: str, user_id: int):
    sql = text("""SELECT id, 
                         name,
                         description,
                         is_public,
                         (SELECT EXISTS (SELECT 1 
                                           FROM category_favourites
                                          WHERE category_id=c.id
                                            AND user_id=:user_id)) AS favourite,
                        (SELECT EXISTS (SELECT 1 
                                          FROM permissions
                                         WHERE user_id=:user_id
                                           AND category_id=c.id)) AS permission
                    FROM categories AS c 
                   WHERE name=:category""")
    category_id = db.session.execute(sql, {"category":category, "user_id":user_id})
    return category_id.fetchone()


def get_threads(category_id: int = None, by_user: int = None,
                user_id: int = None, favourites: bool = False):
    sql = text("""WITH curr_user(role) AS (
        SELECT user_role FROM users WHERE id=:user_id
    )
    SELECT t.id,
                 t.title,
                 t.content,
                 t.link_url,
                 t.visible,
                 COALESCE(likes, 0) AS likes,
                 COALESCE(comments, 0) AS comments,
                 time_ago(t.created_at) AS age,
                 u.username,
                 u.display_name,
                 u.id AS user_id,
                 c.name AS category
            FROM threads AS t
            JOIN categories AS c
              ON c.id=t.category_id
            JOIN users AS u
              ON t.user_id=u.id
            LEFT JOIN (SELECT thread_id, count(*) AS likes
                         FROM thread_likes
                        GROUP BY thread_id
                      ) AS tl
              ON tl.thread_id=t.id
            LEFT JOIN (SELECT thread_id, count(*) AS comments
                         FROM replies
                        GROUP BY thread_id
                      ) AS r
              ON r.thread_id=t.id
            LEFT JOIN permissions AS p
              ON p.category_id=c.id AND p.user_id=:user_id
            LEFT JOIN category_favourites AS cf
              ON cf.category_id=c.id AND cf.user_id=:user_id
           WHERE (c.is_public=:public
                  OR (SELECT role FROM curr_user) > 0
                  OR p.user_id IS NOT NULL)
             AND (:category_id IS NULL OR c.id=:category_id)
             AND (:favourites IS NOT TRUE OR cf.user_id IS NOT NULL)
             AND (:by_user IS NULL OR u.id=:by_user)
             AND (t.visible=:visible OR (SELECT role FROM curr_user) > 0)
           ORDER BY t.created_at DESC;""")
    threads = db.session.execute(sql, {"public":True,
                                       "visible":True,
                                       "category_id":category_id,
                                       "by_user":by_user,
                                       "user_id":user_id,
                                       "favourites":favourites})
    return threads.fetchall()


def get_thread(thread_id: int, user_id: int):
    sql = text("""SELECT t.id,
                         t.title, 
                         t.content, 
                         t.link_url,
                         t.visible,
                         (SELECT count(*)
                            FROM thread_likes AS tl
                           WHERE tl.thread_id=t.id) AS likes,
                         u.username,
                         u.display_name,
                         u.id AS user_id,
                         (SELECT count(*) FROM replies WHERE thread_id=t.id) AS comments,
                         time_ago(t.created_at) AS age, 
                         c.name AS category,
                         (SELECT EXISTS (SELECT *
                                           FROM thread_likes
                                          WHERE user_id=:user_id
                                            AND thread_id=:id)
                         ) AS liked
                    FROM threads AS t
                    JOIN categories AS c
                      ON c.id=t.category_id
                    JOIN users AS u
                      ON t.user_id=u.id
                   WHERE (t.visible=:visible OR (SELECT user_role > 0 
                                                    FROM users 
                                                   WHERE id=:user_id))
                     AND (c.is_public=:public OR (SELECT user_role > 0 
                                                    FROM users 
                                                   WHERE id=:user_id)
                                              OR EXISTS (SELECT 1
                                                           FROM permissions
                                                          WHERE category_id=c.id
                                                            AND user_id=:user_id))
                     AND t.id=:id
                   GROUP BY t.id, u.id, u.display_name, c.name""")
    thread = db.session.execute(sql, {"public":True,
                                      "visible":True,
                                      "id":thread_id,
                                      "user_id":user_id})
    return thread.fetchone()


def get_replies(thread_id: int, user_id: int):
    sql = text("""WITH RECURSIVE reply_tree(
                       id,
                       user_id, 
                       parent_id,
                       content, 
                       created_at,
                       visible,
                       path) 
                    AS (SELECT r.id, 
                               r.user_id, 
                               r.parent_id, 
                               r.content, 
                               r.created_at,
                               r.visible, 
                               ARRAY[r.id]
                          FROM replies AS r
                         WHERE r.parent_id IS NULL
                           AND r.thread_id=:thread_id

                         UNION ALL

                        SELECT r.id, 
                               r.user_id, 
                               r.parent_id, 
                               r.content, 
                               r.created_at,
                               r.visible, 
                               path || r.id
                          FROM replies AS r
                          JOIN reply_tree AS rt
                            ON rt.id=r.parent_id
                         WHERE r.thread_id=:thread_id
                       )
                
                 SELECT rt.id, 
                        rt.user_id, 
                        rt.parent_id, 
                        rt.content,
                        rt.visible,
                        u.username,
                        u.display_name,
                        time_ago(rt.created_at) AS age,
                        (SELECT count(*) 
                           FROM reply_likes AS rl
                          WHERE rl.reply_id=rt.id) AS likes,
                        (SELECT EXISTS (SELECT *
                           FROM reply_likes AS rl
                          WHERE rl.user_id=:user_id
                            AND rl.reply_id=rt.id)
                        ) AS liked,
                        array_length(rt.path, 1)-1 AS depth,
                        rt.path
                   FROM reply_tree AS rt
                   JOIN users AS u
                     ON rt.user_id=u.id
                  ORDER BY path;""")
    replies = db.session.execute(sql, {"thread_id":thread_id, "user_id":user_id})
    return replies.fetchall()


def add_reply(user_id, thread_id, parent_id, content):
    sql = text("""INSERT INTO replies (user_id, thread_id, 
                         parent_id, content) 
                  VALUES (:user_id, :thread_id, :parent_id, :content)""")
    db.session.execute(sql, {"user_id":user_id, "thread_id":thread_id,
                             "parent_id":parent_id, "content":content})
    db.session.commit()


def add_thread(user_id, category_id, link_url, title, content):
    sql = text("""INSERT INTO threads (user_id, category_id, 
                         link_url, title, content)
                  VALUES (:user_id, :category_id, :link_url, :title, :content)""")
    db.session.execute(sql, {"user_id":user_id, "category_id":category_id,
                             "link_url":link_url, "title":title, "content":content})
    db.session.commit()


def toggle_thread_like(user_id: int, thread_id: int):
    sql = text(
        """SELECT 1 FROM thread_likes WHERE user_id=:user_id AND 
        thread_id=:thread_id""")
    like_exists = db.session.execute(sql, {"user_id": user_id,
                                           "thread_id": thread_id}).fetchone()
    if like_exists:
        sql = text(
            """DELETE FROM thread_likes 
                WHERE user_id=:user_id 
                  AND thread_id=:thread_id""")
    else:
        sql = text("""INSERT INTO thread_likes (user_id, thread_id) 
                      VALUES (:user_id, :thread_id)
                          ON CONFLICT DO NOTHING""")
    db.session.execute(sql, {"user_id": user_id, "thread_id": thread_id})
    db.session.commit()
    sql = text(
        """SELECT count(*) FROM thread_likes WHERE thread_id=:thread_id""")
    likes = db.session.execute(sql, {"thread_id": thread_id})
    return likes.fetchone()


def toggle_reply_like(user_id: int, reply_id: int):
    sql = text(
        """SELECT 1 FROM reply_likes 
           WHERE user_id=:user_id AND reply_id=:reply_id""")
    like_exists = db.session.execute(sql, {"user_id": user_id,
                                           "reply_id": reply_id}).fetchone()
    if like_exists:
        sql = text(
            """DELETE FROM reply_likes 
                WHERE user_id=:user_id AND reply_id=:reply_id""")
    else:
        sql = text("""INSERT INTO reply_likes (user_id, reply_id) 
                      VALUES (:user_id, :reply_id)
                          ON CONFLICT DO NOTHING""")
    db.session.execute(sql, {"user_id": user_id, "reply_id": reply_id})
    db.session.commit()
    sql = text("""SELECT count(*) FROM reply_likes WHERE reply_id=:reply_id""")
    likes = db.session.execute(sql, {"reply_id": reply_id})
    return likes.fetchone()


def get_profile(username: str, session_user: int):
    sql = text("""SELECT u.id,
                         u.username, 
                         u.display_name,
                         (SELECT EXISTS (SELECT user_id 
                                           FROM user_followers 
                                          WHERE user_id=u.id
                                            AND follower_id=:follower_id)
                         ) AS followed
                    FROM users AS u 
                   WHERE username=:username""")
    user = db.session.execute(sql, {"username":username,
                                    "follower_id": session_user})
    return user.fetchone()


def get_user_replies(user_id: int, session_user: int):
    sql = text("""SELECT r.id AS reply_id,
                         r.content AS reply_content,
                         count(rl.user_id) AS likes,
                         time_ago(r.created_at) AS reply_age,
                         (SELECT EXISTS (SELECT *
                           FROM reply_likes AS rl
                          WHERE rl.user_id=:session_user
                            AND rl.reply_id=r.id)
                         ) AS liked,
                         t.id AS thread_id,
                         t.title AS thread_title,
                         u2.username AS thread_creator,
                         u2.display_name AS thread_creator_dn,
                         t.content AS thread_content,
                         time_ago(t.created_at) AS thread_age,
                         c.name AS thread_category
                    FROM replies AS r
                    JOIN threads AS t
                      ON t.id=r.thread_id
                    JOIN users AS u
                      ON u.id=r.user_id
                    JOIN users AS u2
                      ON u2.id=t.user_id
                    JOIN categories AS c
                      ON c.id=t.category_id
                         LEFT JOIN reply_likes AS rl
                         ON rl.reply_id=r.id                
                   WHERE u.id=:user_id
                     AND t.visible=:visible
                     AND c.is_public=:is_public
                   GROUP BY r.id, t.id, u2.username, u2.display_name, c.name
                   ORDER BY r.created_at DESC""")
    replies = db.session.execute(sql, {"user_id": user_id, "visible": True,
                                       "is_public": True,
                                       "session_user": session_user})
    return replies.fetchall()


def toggle_user_follow(username: str, follower_id: int):
    user_id = db.session.execute(text("""SELECT id 
                                           FROM users 
                                          WHERE username=:username"""),
                                 {"username": username}).fetchone()[0]
    if not user_id:
        raise ValueError("User not found")
    sql = text("""SELECT 1 FROM user_followers 
                   WHERE user_id=:user_id AND follower_id=:follower_id""")
    already_following = db.session.execute(sql, {"user_id": user_id,
                                                 "follower_id":
                                                     follower_id}).fetchone()
    if already_following:
        sql = text("""DELETE FROM user_followers 
                       WHERE user_id=:user_id AND follower_id=:follower_id
                   RETURNING false""")
    else:
        sql = text("""INSERT INTO user_followers (user_id, follower_id) 
                      VALUES (:user_id, :follower_id)
                          ON CONFLICT DO NOTHING
                   RETURNING true""")
    following = db.session.execute(sql, {"user_id": user_id,
                                         "follower_id": follower_id})
    db.session.commit()
    return following.fetchone()


def get_user_followers(user_id: int):
    sql = text("""SELECT u.username,
                         u.display_name
                    FROM user_followers AS uf
                    JOIN users AS u
                      ON uf.follower_id=u.id
                   WHERE uf.user_id=:user_id""")
    followers = db.session.execute(sql, {"user_id":user_id})
    return followers.fetchall()


def toggle_category_fav(category_name: str, user_id: int):
    category = get_category(category_name, user_id)
    if not category:
        raise ValueError("Category not found")
    sql = text("""SELECT 1 FROM category_favourites 
                   WHERE category_id=:category_id AND user_id=:user_id""")
    already_favourite = db.session.execute(sql, {"category_id": category.id,
                                                 "user_id": user_id}).fetchone()
    if already_favourite:
        sql = text("""DELETE FROM category_favourites
                       WHERE category_id=:category_id 
                         AND user_id=:user_id
                   RETURNING false""")
    else:
        sql = text("""INSERT INTO category_favourites (category_id, user_id) 
                      VALUES (:category_id, :user_id)
                          ON CONFLICT DO NOTHING
                   RETURNING true""")
    favourite = db.session.execute(sql, {"category_id": category.id,
                                         "user_id": user_id})
    db.session.commit()
    return favourite.fetchone()

def create_category(category_name: str, description: str, public: bool):
    sql = text("""SELECT 1 FROM categories WHERE name=:category_name""")
    category_exists = db.session.execute(sql, {
        "category_name": category_name}).fetchone()
    if category_exists:
        raise(ValueError("Category already exists"))
    sql = text("""INSERT INTO categories (name, description, is_public) 
                  VALUES (:category_name, :description, :public)""")
    db.session.execute(sql, {"category_name": category_name,
                             "description": description, "public": public})
    db.session.commit()


def update_category(category_name: str, new_category_name: str,
                    description: str, public: bool):
    sql = text("""SELECT 1 FROM categories WHERE name=:category_name""")
    category_exists = db.session.execute(sql, {
        "category_name": category_name}).fetchone()
    if not category_exists:
        raise(ValueError("Category not found"))
    sql = text("""UPDATE categories 
                     SET name=:new_category_name, 
                         description=:description,
                         is_public=:public
                   WHERE name=:category_name""")
    db.session.execute(sql, {"category_name":category_name,
                             "new_category_name":new_category_name,
                             "description":description,
                             "public":public})
    db.session.commit()


def update_thread(thread_id: int, link_url: str, title: str, content: str,
                  visible: bool):
    sql = text("""SELECT 1 FROM threads WHERE id=:thread_id""")
    thread_exists = db.session.execute(sql, {"thread_id": thread_id}).fetchone()
    if not thread_exists:
        raise (ValueError("Thread not found"))
    sql = text("""UPDATE threads 
                     SET link_url=:link_url,
                         title=:title, 
                         content=:content,
                         visible=(COALESCE(:visible, visible))
                   WHERE id=:thread_id""")
    db.session.execute(sql, {"thread_id": thread_id, "link_url": link_url,
                             "title": title,
                             "content": content, "visible": visible})
    db.session.commit()


def update_reply(reply_id: int, content: str, visible: bool):
    sql = text("""SELECT 1 FROM replies WHERE id=:reply_id""")
    reply_exists = db.session.execute(sql, {"reply_id":reply_id}).fetchone()
    if not reply_exists:
        raise ValueError("Reply not found")
    sql = text("""UPDATE replies
                     SET content=:content,
                         visible=(COALESCE(:visible, visible))
                   WHERE id=:reply_id""")
    db.session.execute(sql, {"reply_id": reply_id, "content": content,
                             "visible": visible})
    db.session.commit()


def users_with_permissions(category_id: int):
    sql = text("""SELECT u.id,
                         u.username,
                         u.display_name
                    FROM users AS u
                    JOIN permissions AS p 
                      ON p.user_id=u.id
                   WHERE p.category_id=:category_id
                   ORDER BY u.username""")
    users = db.session.execute(sql, {"category_id":category_id}).fetchall()
    return users


def users_without_permissions(category_id: int):
    sql = text("""SELECT u.id,
                         u.username,
                         u.display_name
                    FROM users AS u 
                   WHERE NOT EXISTS (SELECT null 
                                       FROM permissions AS p 
                                      WHERE p.user_id=u.id
                                        AND p.category_id=:category_id)
                   ORDER BY u.username""")
    users = db.session.execute(sql, {"category_id":category_id}).fetchall()
    return users


def toggle_permissions(user_id: int, category: str):
    sql = text(
        """SELECT c.id FROM categories AS c, users AS u 
            WHERE c.name=:category AND u.id=:user_id""")
    category_id = db.session.execute(sql, {"user_id": user_id,
                                           "category": category}).fetchone()[0]
    if not category_id:
        raise ValueError("Category or user not found")
    sql = text(
        """SELECT 1 FROM permissions 
            WHERE user_id=:user_id AND category_id=:category_id""")
    approved_user = db.session.execute(sql, {"user_id": user_id,
                                             "category_id":
                                                 category_id}).fetchone()
    if not approved_user:
        sql = text(
            """INSERT INTO permissions (user_id, category_id) 
               VALUES (:user_id, :category_id)""")
    else:
        sql = text(
            """DELETE FROM permissions 
                WHERE user_id=:user_id AND category_id=:category_id""")
    db.session.execute(sql, {"user_id": user_id, "category_id": category_id})
    db.session.commit()
