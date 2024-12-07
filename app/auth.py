from flask import render_template, redirect, request, session, url_for, flash
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash

from app import app
from . import users
from .content import register_user
from .db import db
from .forms import RegistrationForm, LoginForm


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if not users.login(form.username.data, form.password.data):
            flash("Wrong username or password", "error")
            return render_template("login.html", form=form)
        flash("Login successful", "success")
        if request.args.get("next"):
            return redirect(request.args.get("next"))
        return redirect(url_for("index"))
    return render_template("login.html", form=form)


@app.route("/logout")
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
        registered = register_user(form.username.data, form.display_name.data, hashed_password)
        if registered:
            flash("Registration successful.", "success")
            return redirect(url_for("login"))
        else:
            flash("Registration failed.", "error")
            return redirect(url_for("register"))
    return render_template("register.html", form=form)
