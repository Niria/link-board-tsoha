from app import app
from flask import render_template, redirect, request, session, url_for
from sqlalchemy.sql import text
from .db import db
from werkzeug.security import check_password_hash, generate_password_hash


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        sql = text("SELECT id, password, username, display_name FROM users WHERE username=:username")
        result = db.session.execute(sql, {"username":username})
        user = result.fetchone()
        if not user:
            return render_template("error.html", message="Invalid username"), 401
        else:
            hashed_pw = user.password
            if check_password_hash(hashed_pw, password):
                session["username"] = user.username
                session["display_name"] = user.display_name
                session["user_id"] = user.id
                if request.form.get("next"):
                    return redirect(request.form["next"])
            else:
                return render_template("error.html", message="Invalid password"), 401
        return redirect(url_for("index"))

@app.route("/logout")
def logout():
    del session["username"]
    del session["display_name"]
    del session["user_id"]
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2:
            return render_template("error.html", message="Passwords don't match")
        if len(username) < 3 or len(username) > 20:
            return render_template("error.html", 
                                   message="Username must be between 3 and 20 characters long.")
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