from .db import db
from sqlalchemy.sql import text


def get_category_list():
    sql = text("""SELECT c.name
                    FROM categories AS c
                   WHERE c.is_public=:public""")
    categories = db.session.execute(sql, {"public":True})
    return categories.fetchall()

def get_all_threads():
    sql = text("""SELECT t.title, t.content, t.link_url, c.name 
                    FROM threads AS t 
                    JOIN categories AS c 
                      ON c.id=t.category_id 
                   WHERE c.is_public=:public""")
    
    threads = db.session.execute(sql, {"public":True})
    return threads.fetchall()

def get_category_threads(category):
    sql = text("""SELECT t.title, t.content, t.link_url, c.name 
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
    sql = text("""SELECT t.title, t.content, t.link_url
                    FROM threads AS t
                    JOIN replies AS r 
                      ON t.id=r.thread_id
                    JOIN categories AS c
                      ON c.id=t.category_id
                   WHERE t.visible=:visible
                     AND c.is_public=:public
                     AND t.id=:id""")
    thread = db.session.execute(sql, {"visible":True, 
                                      "is_public":True, 
                                      "id":id})
    return thread