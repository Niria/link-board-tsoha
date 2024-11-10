from .db import db
from sqlalchemy.sql import text


def get_category_list():
    sql = text("""SELECT c.name
                    FROM categories AS c
                   WHERE c.is_public=:public""")
    categories = db.session.execute(sql, {"public":True})
    return categories.fetchall()

                        #  date_trunc('second', CURRENT_TIMESTAMP-t.created_at) AS age, 
def get_threads(category: str):
    sql = text("""SELECT t.id, t.title, t.content, t.link_url, t.likes,
                         u.display_name, count(r.id) AS comments, 
                         time_ago(t.created_at) AS age,
                         c.name AS category
                    FROM threads AS t 
                    JOIN categories AS c 
                      ON c.id=t.category_id 
                    JOIN users AS u
                      ON t.user_id=u.id
                    LEFT JOIN replies AS r
                      ON r.thread_id=t.id
                   WHERE c.is_public=:public
                     AND (:category IS NULL OR c.name=:category)
                     AND t.visible=:visible
                   GROUP BY t.id, u.display_name, c.name
                   ORDER BY t.created_at DESC""")
    
    threads = db.session.execute(sql, {"public":True, 
                                       "visible":True, 
                                       "category":category})
    return threads.fetchall()

def get_thread(id: int):
    sql = text("""SELECT t.id,
                         t.title, 
                         t.content, 
                         t.link_url, 
                         c.name AS category,
                         u.display_name,
                         u.id AS user_id
                    FROM threads AS t
                    JOIN categories AS c
                      ON c.id=t.category_id
                    JOIN users AS u
                      ON t.user_id=u.id
                   WHERE t.visible=:visible
                     AND c.is_public=:public
                     AND t.id=:id""")
    thread = db.session.execute(sql, {"visible":True, 
                                      "public":True, 
                                      "id":id})
    return thread.fetchone()

def get_replies(thread_id: int, order=""):
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
                        array_length(rt.path, 1)-1 AS depth,
                        rt.path
                   FROM reply_tree AS rt
                   JOIN users AS u
                     ON rt.user_id=u.id
                  ORDER BY path;""")
    replies = db.session.execute(sql, {"thread_id":thread_id})
    return replies.fetchall()

def add_reply(user_id, thread_id, parent_id, content):
    sql = text("""INSERT INTO replies (user_id, thread_id, 
                         parent_id, content) 
                  VALUES (:user_id, :thread_id, :parent_id, :content)""") 
    db.session.execute(sql, {"user_id":user_id, "thread_id":thread_id,
                             "parent_id":parent_id, "content":content})
    db.session.commit()