from .db import db
from sqlalchemy.sql import text


def get_category_list():
    sql = text("""SELECT c.name
                    FROM categories AS c
                   WHERE c.is_public=:public""")
    categories = db.session.execute(sql, {"public":True})
    return categories.fetchall()

def get_category_id(category: str):
    sql = text("""SELECT id FROM categories WHERE name=:category""")
    category_id = db.session.execute(sql, {"category":category})
    return category_id.fetchone()

# TODO: Count queries should be cleaned
def get_threads(category: str):
    if category:
        sql = text("SELECT 1 FROM categories WHERE name=:category")
        category_exists = db.session.execute(sql, {"category":category})
        if not category_exists:
            return None
    sql = text("""SELECT t.id, 
                         t.title, 
                         t.content, 
                         t.link_url,
                         (SELECT count(*)
                            FROM thread_likes AS tl
                           WHERE tl.thread_id=t.id) AS likes,
                         count(r.id) AS comments, 
                         time_ago(t.created_at) AS age,
                         u.display_name, u.id AS user_id,
                         c.name AS category
                    FROM threads AS t 
                    JOIN categories AS c 
                      ON c.id=t.category_id 
                    JOIN users AS u
                      ON t.user_id=u.id
                         LEFT JOIN replies AS r
                         ON r.thread_id=t.id
                         LEFT JOIN thread_likes AS tl
                         ON tl.thread_id=t.id
                   WHERE c.is_public=:public
                     AND (:category IS NULL OR c.name=:category)
                     AND t.visible=:visible
                   GROUP BY t.id, u.id, u.display_name, c.name
                   ORDER BY t.created_at DESC""")
    threads = db.session.execute(sql, {"public":True, 
                                       "visible":True, 
                                       "category":category})
    return threads.fetchall()

# TODO: combine getting all and single threads into one function?
# TODO: Count queries should be cleaned
def get_thread(thread_id: int, user_id: int):
    sql = text("""SELECT t.id,
                         t.title, 
                         t.content, 
                         t.link_url,
                         (SELECT count(*)
                            FROM thread_likes AS tl
                           WHERE tl.thread_id=t.id) AS likes,
                         u.display_name,
                         u.id AS user_id,
                         count(r.id) AS comments,
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
                         LEFT JOIN replies AS r
                         ON r.thread_id=t.id
                         LEFT JOIN thread_likes AS tl
                         ON t.id=tl.thread_id
                   WHERE t.visible=:visible
                     AND c.is_public=:public
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
                       path) 
                    AS (SELECT r.id, 
                               r.user_id, 
                               r.parent_id, 
                               r.content, 
                               r.created_at, 
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
    sql = text("""SELECT 1 FROM thread_likes WHERE user_id=:user_id AND thread_id=:thread_id""")
    like_exists = db.session.execute(sql, {"user_id":user_id, "thread_id":thread_id}).fetchone()
    if like_exists:
        sql = text("""DELETE FROM thread_likes WHERE user_id=:user_id AND thread_id=:thread_id""")
        db.session.execute(sql, {"user_id":user_id, "thread_id":thread_id})
        db.session.commit()
    else:
        sql = text("""INSERT INTO thread_likes (user_id, thread_id) 
                    VALUES (:user_id, :thread_id)
                            ON CONFLICT DO NOTHING""")
        db.session.execute(sql, {"user_id":user_id, "thread_id":thread_id})
        db.session.commit()
    sql = text("""SELECT count(*) FROM thread_likes WHERE thread_id=:thread_id""")
    likes = db.session.execute(sql, {"thread_id":thread_id})
    return likes.fetchone()

def toggle_reply_like(user_id: int, reply_id: int):
    sql = text("""SELECT 1 FROM reply_likes WHERE user_id=:user_id AND reply_id=:reply_id""")
    like_exists = db.session.execute(sql, {"user_id":user_id, "reply_id":reply_id}).fetchone()
    if like_exists:
        sql = text("""DELETE FROM reply_likes WHERE user_id=:user_id AND reply_id=:reply_id""")
        db.session.execute(sql, {"user_id":user_id, "reply_id":reply_id})
        db.session.commit()
    else:
        sql = text("""INSERT INTO reply_likes (user_id, reply_id) 
                    VALUES (:user_id, :reply_id)
                            ON CONFLICT DO NOTHING""")
        db.session.execute(sql, {"user_id":user_id, "reply_id":reply_id})
        db.session.commit()
    sql = text("""SELECT count(*) FROM reply_likes WHERE reply_id=:reply_id""")
    likes = db.session.execute(sql, {"reply_id":reply_id})
    return likes.fetchone()
