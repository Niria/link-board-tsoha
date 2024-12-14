from sqlalchemy import text

from app.utils.db import db


def get_threads(category_id: int = None, by_user: int = None,
                user_id: int = None, favourites: bool = False):
    sql = text("""
        WITH curr_user(is_admin) AS (
           SELECT user_role > 0 FROM users WHERE id=:user_id
        )
        SELECT t.id,
               t.title,
               t.content,
               t.link_url,
               t.visible,
               t.thumbnail,
               COALESCE(likes, 0) AS likes,
               COALESCE(comments, 0) AS comments,
               to_char(t.created_at, 'DD.MM.YYYY HH24:MI:SS UTC OF (TZ)') as created_at,
               time_ago(t.created_at) AS age,
               to_char(t.updated_at, 'DD.MM.YYYY HH24:MI:SS UTC OF (TZ)') AS updated_at,
               (CASE WHEN t.updated_at IS NULL 
                     THEN null 
                     ELSE time_ago(t.updated_at) END
               ) AS edited,
               (CASE WHEN uf.user_id IS NULL
                     THEN false
                     ELSE true END) AS following,
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
            ON p.category_id=c.id 
           AND p.user_id=:user_id
          LEFT JOIN category_favourites AS cf
            ON cf.category_id=c.id 
           AND cf.user_id=:user_id
          LEFT JOIN user_followers AS uf
            ON uf.user_id=u.id
           AND uf.follower_id=:user_id
         WHERE (c.is_public=:public
               OR (SELECT is_admin FROM curr_user)
               OR p.user_id IS NOT NULL)
           AND (:category_id IS NULL OR c.id=:category_id)
           AND (:favourites IS NOT TRUE OR cf.user_id IS NOT NULL)
           AND (:by_user IS NULL OR u.id=:by_user)
           AND (t.visible=:visible OR (SELECT is_admin FROM curr_user))
         ORDER BY t.created_at DESC;
    """)
    threads = db.session.execute(sql, {"public":True,
                                       "visible":True,
                                       "category_id":category_id,
                                       "by_user":by_user,
                                       "user_id":user_id,
                                       "favourites":favourites})
    return threads.fetchall()


def get_thread(thread_id: int, user_id: int):
    sql = text("""
        WITH curr_user(is_admin) AS (
            SELECT user_role > 0 FROM users WHERE id=:user_id
        )
        SELECT t.id,
               t.title,
               t.content,
               t.link_url,
               t.visible,
               COALESCE(likes, 0) AS likes,
               u.username,
               u.display_name,
               u.id AS user_id,
               (SELECT count(*) FROM replies WHERE thread_id=:id) AS comments,
               to_char(t.created_at, 'DD.MM.YYYY HH24:MI:SS UTC OF (TZ)') as created_at,
               time_ago(t.created_at) AS age,
               to_char(t.updated_at, 'DD.MM.YYYY HH24:MI:SS UTC OF (TZ)') AS updated_at,
               (CASE WHEN t.updated_at IS NULL 
                THEN null 
                ELSE time_ago(t.updated_at) END
               ) AS edited,
               c.name AS category,
               (CASE WHEN tl.user_id IS NULL THEN false ELSE true END) AS liked,
               (CASE WHEN uf.user_id IS NULL THEN false ELSE true END) AS following,
               thumbnail
          FROM threads AS t
          JOIN categories AS c
            ON c.id=t.category_id
          JOIN users AS u
            ON t.user_id=u.id
               LEFT JOIN (SELECT thread_id, count(*) AS likes
                            FROM thread_likes
                           GROUP BY thread_id) AS all_likes
                 ON all_likes.thread_id=t.id
               LEFT JOIN thread_likes AS tl
                 ON tl.thread_id=t.id 
                AND tl.user_id=:user_id
               LEFT JOIN permissions AS p
                 ON p.category_id=c.id 
                AND p.user_id=:user_id
               LEFT JOIN user_followers AS uf
                 ON uf.user_id=u.id 
                AND uf.follower_id=:user_id
         WHERE (t.visible=:visible OR (SELECT is_admin FROM curr_user))
           AND (c.is_public=:public
               OR (SELECT is_admin FROM curr_user)
                OR p.user_id IS NOT NULL)
           AND t.id=:id;
       """)
    thread = db.session.execute(sql, {"public":True,
                                      "visible":True,
                                      "id":thread_id,
                                      "user_id":user_id})
    return thread.fetchone()


def get_replies(thread_id: int, user_id: int):
    sql = text("""
        WITH RECURSIVE reply_tree(
             id,
             user_id, 
             parent_id,
             content, 
             created_at,
             updated_at,
             visible,
             path) 
          AS (SELECT r.id, 
                     r.user_id, 
                     r.parent_id, 
                     r.content, 
                     r.created_at,
                     r.updated_at,
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
                     r.updated_at,
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
               to_char(rt.created_at, 'DD.MM.YYYY HH24:MI:SS UTC OF (TZ)') as created_at,
               time_ago(rt.created_at) AS age,
               to_char(rt.updated_at, 'DD.MM.YYYY HH24:MI:SS UTC OF (TZ)') as updated_at,
               (CASE WHEN rt.updated_at IS NULL 
                THEN null 
                ELSE time_ago(rt.updated_at) END
               ) AS edited,
               COALESCE(likes, 0) AS likes,
               (CASE WHEN rl.user_id IS NULL 
                     THEN false 
                     ELSE true END) AS liked,
               (CASE WHEN uf.user_id IS NULL
                     THEN false
                     ELSE true END) AS following,
               array_length(rt.path, 1)-1 AS depth,
               rt.path
          FROM reply_tree AS rt
          JOIN users AS u
            ON rt.user_id=u.id
               LEFT JOIN (SELECT reply_id, count(*) AS likes 
                            FROM reply_likes 
                           GROUP BY reply_id) AS all_likes 
                 ON all_likes.reply_id=rt.id
               LEFT JOIN reply_likes AS rl 
                 ON rl.reply_id=rt.id 
                AND rl.user_id=:user_id
               LEFT JOIN user_followers AS uf
                 ON uf.user_id=u.id
                AND uf.follower_id=:user_id
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


def add_thread(user_id, category_id, link_url, title, content, thumbnail):
    sql = text("""INSERT INTO threads (user_id, category_id, 
                         link_url, title, content, thumbnail) 
                  VALUES (:user_id, :category_id, :link_url, :title, :content, :thumbnail)""")
    db.session.execute(sql, {"user_id":user_id, "category_id":category_id,
                             "link_url":link_url, "title":title,
                             "content":content, "thumbnail":thumbnail})
    db.session.commit()


def toggle_thread_like(user_id: int, thread_id: int):
    sql = text(
        """SELECT 1 FROM thread_likes 
            WHERE user_id=:user_id AND thread_id=:thread_id""")
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


def update_thread(thread_id: int, link_url: str, title: str, content: str,
                  visible: bool, thumbnail: bytearray, update_thumbnail: bool):
    sql = text("""SELECT 1 FROM threads WHERE id=:thread_id""")
    thread_exists = db.session.execute(sql, {"thread_id": thread_id}).fetchone()
    if not thread_exists:
        raise (ValueError("Thread not found"))
    sql = text("""UPDATE threads 
                     SET link_url=:link_url,
                         title=:title, 
                         content=:content,
                         visible=(COALESCE(:visible, visible)),
                         thumbnail = CASE WHEN :update_thumbnail THEN :thumbnail ELSE thumbnail END
                   WHERE id=:thread_id""")
    db.session.execute(sql, {"thread_id": thread_id, "link_url": link_url,
                             "title": title,
                             "content": content, "visible": visible,
                             "thumbnail": thumbnail, "update_thumbnail": update_thumbnail})
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
