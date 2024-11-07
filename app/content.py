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
    sql = text("""SELECT r.user_id,
                         r.parent_id,
                         r.content, 
                         u.display_name
                    FROM replies AS r
                    JOIN threads AS t
                      ON t.id=r.thread_id
                    JOIN users AS u
                      ON u.id=r.user_id
                   WHERE t.id=:thread_id""")
    replies = db.session.execute(sql, {"thread_id":thread_id})
    return replies.fetchall()