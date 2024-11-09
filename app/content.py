from .db import db
from sqlalchemy.sql import text


def get_category_list():
    sql = text("""SELECT c.name
                    FROM categories AS c
                   WHERE c.is_public=:public""")
    categories = db.session.execute(sql, {"public":True})
    return categories.fetchall()

def get_all_threads():
    sql = text("""SELECT t.id, t.title, t.content, t.link_url, c.name AS category
                    FROM threads AS t 
                    JOIN categories AS c 
                      ON c.id=t.category_id 
                   WHERE c.is_public=:public
                     AND t.visible=:visible""")
    
    threads = db.session.execute(sql, {"public":True, "visible":True})
    return threads.fetchall()

def get_category_threads(category):
    sql = text("""SELECT t.id, t.title, t.content, t.link_url, c.name AS category
                    FROM threads AS t 
                    JOIN categories AS c 
                      ON c.id=t.category_id 
                   WHERE c.is_public=:public
                     AND c.name=:category
                     AND t.visible=:visible""")
    
    threads = db.session.execute(sql, {"public":True, 
                                       "category":category, 
                                       "visible":True})
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

def get_replies(thread_id: int):
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
                               ARRAY[r.id, r.id]
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
                        u.display_name,
                        array_length(path, 1)-2 AS depth
                   FROM reply_tree AS rt
                   JOIN users AS u
                     ON rt.user_id=u.id
                  ORDER BY path[1:array_length(path, 1)-1],
                        created_at ASC;""")
    replies = db.session.execute(sql, {"thread_id":thread_id})
    return replies.fetchall()

def add_reply(user_id, thread_id, parent_id, content):
    sql = text("""INSERT INTO replies (user_id, thread_id, 
                         parent_id, content) 
                  VALUES (:user_id, :thread_id, :parent_id, :content)""") 
    db.session.execute(sql, {"user_id":user_id, "thread_id":thread_id,
                             "parent_id":parent_id, "content":content})
    db.session.commit()