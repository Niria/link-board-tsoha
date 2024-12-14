from sqlalchemy.exc import SQLAlchemyError

from app.utils.db import db
from sqlalchemy.sql import text


def get_profile(username: str, session_user: int):
    sql = text("""SELECT u.id,
                         u.username, 
                         u.display_name,
                         COALESCE(u.description, '') AS description,
                         u.profile_public,
                         to_char(u.created_at, 'DD.MM.YYYY') as join_date,
                         u.created_at,
                         to_char(u.updated_at, 'DD.MM.YYYY HH24:MI:SS UTC OF (TZ)') as updated_at,
                         u.updated_at,
                         (SELECT EXISTS (SELECT user_id 
                                           FROM user_followers 
                                          WHERE user_id=u.id
                                            AND follower_id=:session_user) 
                         ) AS followed,
                         COALESCE(followers, 0) AS followers,
                         COALESCE(threads, 0) AS threads,
                         COALESCE(replies, 0) AS replies
                    FROM users AS u
                         LEFT JOIN (SELECT user_id, count(*) AS followers
                                      FROM user_followers AS uf
                                      JOIN users AS u
                                        ON u.id=uf.follower_id
                                     GROUP BY user_id) AS fc
                           ON fc.user_id=u.id
                         LEFT JOIN (SELECT user_id, count(*) AS threads
                                      FROM threads
                                     GROUP BY user_id) AS t 
                           ON t.user_id=u.id
                         LEFT JOIN (SELECT user_id, count(*) AS replies
                                      FROM replies
                                     GROUP BY user_id) AS r 
                           ON r.user_id=u.id
                   WHERE username=:username""")
    user = db.session.execute(sql, {"username":username,
                                    "session_user": session_user})
    return user.fetchone()


def get_user_replies(user_id: int, session_user: int):
    sql = text("""SELECT r.id AS reply_id,
                         r.content AS reply_content,
                         count(rl.user_id) AS likes,
                         time_ago(r.created_at) AS reply_age,
                         to_char(t.created_at, 'DD.MM.YYYY HH24:MI:SS UTC OF (TZ)') as created_at,
                         (CASE WHEN r.updated_at IS NULL 
                          THEN null 
                          ELSE time_ago(r.updated_at) END
                         ) AS edited,
                         to_char(r.updated_at, 'DD.MM.YYYY HH24:MI:SS UTC OF (TZ)') as updated_at,
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
                   WHERE uf.user_id=:user_id
                     AND u.profile_public=true""")
    followers = db.session.execute(sql, {"user_id":user_id})
    return followers.fetchall()


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


def update_profile(user_id: int, display_name: str, description: str, is_public: bool):
    sql = text("""UPDATE users 
                     SET display_name=:display_name,
                         description=:description,
                         profile_public=(COALESCE(:is_public, profile_public))
                   WHERE id=:user_id
    """)
    db.session.execute(sql, {"user_id": user_id, "display_name": display_name,
                             "description": description, "is_public": is_public})
    db.session.commit()


def register_user(username: str, display_name: str, password: str):
    sql = text("""INSERT INTO users (username, display_name, password) 
                  VALUES (:username, :display_name, :password)""")
    try:
        db.session.execute(sql,
                           {"username": username,
                            "display_name": display_name,
                            "password": password})
        db.session.commit()
        return True
    except SQLAlchemyError:
        return False


def get_user(username):
    sql = text("""SELECT id, 
                         password, 
                         username, 
                         display_name,
                         user_role
                    FROM users 
                   WHERE username=:username""")
    return db.session.execute(sql, {"username": username}).fetchone()


