from flask import render_template, redirect, session, url_for, flash
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash, check_password_hash

from app import app
from app.services import users as user_service
from app.utils.db import db
from app.utils.forms import RegistrationForm, LoginForm
from app.utils.decorators import login_required


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = user_service.get_user(form.username.data)
        if not user or not check_password_hash(user.password, form.password.data):
            flash("Wrong username or password", "error")
            return render_template("login.html", form=form)

        session["username"] = user.username
        session["display_name"] = user.display_name
        session["user_id"] = user.id
        session["user_role"] = user.user_role
        flash("Login successful", "success")
        return redirect(url_for("index"))
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    del session["username"]
    del session["display_name"]
    del session["user_id"]
    del session["user_role"]
    flash("You have been logged out", "success")
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        sql = text("""SELECT id FROM users WHERE username=:username""")
        user = db.session.execute(sql, {"username": form.username.data}).fetchone()
        if user:
            flash("Username already in use.", "error")
            return render_template("register.html", form=form)
        hashed_password = generate_password_hash(form.password.data)
        registered = user_service.register_user(form.username.data, form.display_name.data, hashed_password)
        if registered:
            flash("Registration successful.", "success")
            return redirect(url_for("login"))
        else:
            flash("Registration failed.", "error")
            return redirect(url_for("register"))
    return render_template("register.html", form=form)
