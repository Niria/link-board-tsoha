from .db import db
from sqlalchemy.sql import text


def get_categories():
    sql = text("""SELECT c.name
                    FROM categories AS c
                   WHERE c.is_public=:public""")
    categories = db.session.execute(sql, {"public":True})
    return categories.fetchall()

def get_category(name: str):
    sql = text("""SELECT c.name, t.title, t.content, t.link_url
                    FROM categories AS c
                    JOIN threads AS t
                      ON c.id=t.category_id
                   WHERE c.name=:name
                     AND t.visible=:visible""")
    category = db.session.execute(sql, {"name":name, "visible":True})
    return category.fetchall()

def get_threads():
    sql = text("""SELECT t.title 
                    FROM threads AS t 
                    JOIN categories AS c 
                      ON c.id=t.category_id 
                   WHERE c.is_public=:public""")
    
    threads = db.session.execute(sql, {"public":True})
    return threads.fetchall()