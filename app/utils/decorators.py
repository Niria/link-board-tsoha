from functools import wraps
from flask import session, redirect, url_for, render_template


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
