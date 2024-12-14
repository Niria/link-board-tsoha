from sqlalchemy import text

from app.utils.db import db


def keyword_search(search_type: str, keyword: str, user_id: int):
    match search_type:
        case "user":
            sql = text("""
                WITH curr_user(is_admin) AS (
                     SELECT user_role > 0 FROM users WHERE id=:user_id
                )           
                SELECT u.username, 
                       u.display_name,
                       to_char(u.created_at, 'DD.MM.YYYY') as join_date,
                       COALESCE(threads, 0) AS threads,
                       COALESCE(replies, 0) AS replies,
                       (CASE WHEN uf.follower_id IS NULL
                        THEN false ELSE true END) AS following
                  FROM users AS u
                       LEFT JOIN (SELECT t.user_id, count(*) AS threads
                                    FROM threads AS t 
                                   GROUP BY t.user_id) AS tc
                         ON tc.user_id=u.id
                       LEFT JOIN (SELECT r.user_id, count(*) AS replies
                                    FROM replies AS r
                                   GROUP BY r.user_id) AS rc
                         ON rc.user_id=u.id
                       LEFT JOIN user_followers AS uf
                         ON uf.user_id=u.id
                        AND uf.follower_id=:user_id
                 WHERE (u.username ILIKE '%' || :keyword || '%'
                        OR u.display_name ILIKE '%' || :keyword || '%')
                   AND (profile_public=true OR (SELECT is_admin FROM curr_user))
                 ORDER BY u.username""")
        case "category":
            sql = text("""SELECT c.name,
                                 COALESCE(c.description, '') AS description,
                                 c.is_public,
                                 to_char(c.created_at, 'DD.MM.YYYY') as creation_date,
                                 COALESCE(threads, 0) AS threads,
                                 COALESCE(favourites, 0) AS favourites,
                                 (CASE WHEN cf.user_id IS NULL
                                       THEN false ELSE true END) AS favourited
                            FROM categories AS c
                                 LEFT JOIN (SELECT t.category_id, count(*) AS threads
                                              FROM threads AS t
                                             GROUP BY t.category_id) AS tc
                                   ON tc.category_id=c.id
                                 LEFT JOIN (SELECT cf.category_id, count(*) AS favourites
                                              FROM category_favourites AS cf 
                                             GROUP BY cf.category_id) AS fc
                                   ON fc.category_id=c.id
                                 LEFT JOIN category_favourites AS cf 
                                   ON cf.category_id=c.id
                                  AND cf.user_id=:user_id
                           WHERE c.name ILIKE '%' || :keyword || '%'
                           ORDER BY threads DESC, favourites DESC, c.name""")
        case "thread":
            sql = text("""
            WITH curr_user(is_admin) AS (
                 SELECT user_role > 0 FROM users WHERE id=:user_id
            ) 
            SELECT t.id,
                   t.title, 
                   t.link_url,
                   t.visible,
                   t.thumbnail,
                   COALESCE(likes, 0) AS likes,
                   COALESCE(comments, 0) AS comments,
                   to_char(t.created_at, 'DD.MM.YYYY') as creation_date,
                   u.username,
                   u.display_name,
                   c.name AS category
              FROM threads AS t
              JOIN categories AS c
                ON c.id=t.category_id
              JOIN users AS u
                ON u.id=t.user_id
                   LEFT JOIN (SELECT tf.thread_id, count(*) AS likes
                                FROM thread_likes AS tf
                               GROUP BY tf.thread_id) AS tl
                     ON tl.thread_id=t.id
                   LEFT JOIN (SELECT r.thread_id, count(*) AS comments
                                FROM replies AS r 
                               GROUP BY r.thread_id) AS rc
                     ON rc.thread_id=t.id
             WHERE t.title ILIKE '%' || :keyword || '%'
               AND (t.visible OR (SELECT is_admin FROM curr_user))
             ORDER BY t.created_at DESC""")
        case _:
            raise ValueError("Invalid search type")
    result = db.session.execute(sql, {"keyword": keyword, "user_id": user_id}).fetchall()
    return result
