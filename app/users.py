from flask import session, request, abort
from sqlalchemy.sql import text
from .db import db
from werkzeug.security import check_password_hash
import secrets


# TODO: turn into a decorator?
# TODO: move all csrf tokens to headers instead of using forms?
def check_csrf():
    if session["csrf_token"] != request.headers.get('csrf-token') \
        and session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

def login(username, password):
    sql = text("SELECT id, password, username, display_name FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        return False
    if not check_password_hash(user.password, password):
        return False
    session["username"] = user.username
    session["display_name"] = user.display_name
    session["user_id"] = user.id
    session["csrf_token"] = secrets.token_hex(16)
    return True
    