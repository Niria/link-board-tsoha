from sqlalchemy import text

from app.utils.db import db


def get_category_list(user_id: int = None):
    sql = text("""
        SELECT c.name
          FROM categories AS c
               LEFT JOIN permissions AS p
                 ON p.category_id=c.id AND p.user_id=:user_id
               LEFT JOIN category_favourites AS cf
                 ON cf.category_id=c.id AND cf.user_id=:user_id
               LEFT JOIN (SELECT category_id, count(*) AS threads
                            FROM threads
                           GROUP BY category_id) AS t
                 ON t.category_id=c.id
         WHERE (c.is_public=:public 
               OR (SELECT user_role > 0 
                    FROM users 
                   WHERE id=:user_id)
               OR p.user_id IS NOT NULL)
         ORDER BY cf.user_id, threads DESC NULLS LAST, c.name
         LIMIT 12;""")
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


def update_category(category_id: int, new_category_name: str,
                    description: str, public: bool):
    sql = text("""UPDATE categories 
                     SET name=:new_category_name, 
                         description=:description,
                         is_public=:public
                   WHERE id=:category_id""")
    db.session.execute(sql, {"category_id":category_id,
                             "new_category_name":new_category_name,
                             "description":description,
                             "public":public})
    db.session.commit()
