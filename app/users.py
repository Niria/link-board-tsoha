import secrets
from functools import wraps

from flask import session, redirect, url_for, render_template
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash

from .db import db


def login(username, password):
    sql = text("""SELECT id, 
                         password, 
                         username, 
                         display_name,
                         user_role
                    FROM users 
                   WHERE username=:username""")
    user = db.session.execute(sql, {"username": username}).fetchone()
    if not user:
        return False
    if not check_password_hash(user.password, password):
        return False
    session["username"] = user.username
    session["display_name"] = user.display_name
    session["user_id"] = user.id
    session["user_role"] = user.user_role
    session["csrf_token"] = secrets.token_hex(16)
    return True


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_role") < 1:
            return render_template("error.html",
                                   message="Unauthorised.")
        return f(*args, **kwargs)

    return decorated_function
