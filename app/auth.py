from app import app
from flask import render_template, redirect, request, session, url_for
from sqlalchemy.sql import text
from .db import db
from . import users
from werkzeug.security import generate_password_hash


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not users.login(username, password):
            return render_template("error.html", message="Wrong username or password."), 401
        if request.form.get("next"):
            return redirect(request.form["next"])
        return redirect(url_for("index"))


@app.route("/logout")
def logout():
    del session["username"]
    del session["display_name"]
    del session["user_id"]
    del session["user_role"]
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
        if password1 != password2:
            return render_template("error.html", message="Passwords don't match")
        if len(username) < 3 or len(username) > 20:
            return render_template("error.html", 
                                   message="Username must be between 3 and 20 characters long.")
        if len(display_name) < 3 or len(display_name) > 20:
            return render_template("error.html", 
                                   message="Display name must be between 3 and 20 characters long.")
        if len(password1) < 4 or len(password1) > 64:
            return render_template("error.html", 
                                   message="Password must be between 4 and 64 characters long.")
        
        sql = text("SELECT id FROM users WHERE username=:username")
        user = db.session.execute(sql, {"username":username}).fetchone()
        if user:
            return render_template("error.html", message="Username already exists.")
        
        hashed_password = generate_password_hash(password1)
        sql = text("INSERT INTO users (username, password) VALUES (:username, :password)")
        db.session.execute(sql, {"username":username, "password":hashed_password})
        db.session.commit()
        return redirect(url_for("index"))