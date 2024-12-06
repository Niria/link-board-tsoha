from flask import render_template, redirect, request, session, url_for, flash
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash

from app import app
from . import users
from .db import db


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not users.login(username, password):
            flash("Wrong username or password.", "error")
            return redirect(url_for("login"))
        if request.form.get("next"):
            return redirect(request.form["next"])
        return redirect(url_for("index"))


@app.route("/logout")
def logout():
    del session["username"]
    del session["display_name"]
    del session["user_id"]
    del session["user_role"]
    del session["csrf_token"]
    return redirect(url_for("login"))


# TODO: move db requests to another module/function
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        display_name = request.form["displayname"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        redirect_user = False
        if password1 != password2:
            flash("Passwords don't match.", "error")
            redirect_user = True
        if len(username) < 3 or len(username) > 20:
            flash("Username must be between 3 and 20 characters.", "error")
            redirect_user = True
        if len(display_name) < 3 or len(display_name) > 20:
            flash("Display name must be between 3 and 20 characters.", "error")
            redirect_user = True
        if " " in username or " " in display_name:
            flash("Names cannot contain spaces.", "error")
            redirect_user = True
        if len(password1) < 4 or len(password1) > 64:
            flash("Password must be between 8 and 64 characters.", "error")
            redirect_user = True
        if redirect_user:
            return redirect(url_for("register"))
        sql = text("""SELECT id FROM users WHERE username=:username""")
        user = db.session.execute(sql, {"username": username}).fetchone()
        if user:
            flash("Username already in use.", "error")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password1)
        sql = text("""INSERT INTO users (username, display_name, password) 
                      VALUES (:username, :display_name, :password)""")
        db.session.execute(sql,
                           {"username": username,
                            "display_name": display_name,
                            "password": hashed_password})
        db.session.commit()
        flash("Registration successful.", "success")
        return redirect(url_for("login"))
