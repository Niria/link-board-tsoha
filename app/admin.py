from app import app
from flask import render_template, redirect, request, session, url_for
from sqlalchemy.sql import text

from .content import create_category, get_category, update_category
from .db import db
from . import users
from werkzeug.security import generate_password_hash

from .users import admin_required, check_csrf


@app.route("/new_category", methods=["GET", "POST"])
@admin_required
def new_category():
    if request.method == "GET":
        return render_template("category_form.html")
    if request.method == "POST":
        check_csrf()
        category_name = request.form["category_name"]
        public = True if request.form["public"] == "true" else False
        create_category(category_name, public)
        return redirect(url_for("index"))


@app.route("/c/<string:category>/edit", methods=["GET", "POST"])
@admin_required
def edit_category(category):
    if request.method == "GET":
        category = get_category(category, session["user_id"])
        return render_template("category_form.html", category=category)
    if request.method == "POST":
        check_csrf()
        new_category_name = request.form["category_name"]
        public = True if request.form["public"] == "true" else False
        update_category(category, new_category_name, public)
        return redirect(url_for("index"))


@app.route("/p/<int:thread_id>/edit", methods=["POST"])
@admin_required
def edit_thread(thread_id):
    pass



@app.route("/p/<int:thread_id>/<int:reply_id>/edit", methods=["POST"])
@admin_required
def edit_reply(thread_id, reply_id):
    pass


@app.route("/u/<int:user_id>/edit", methods=["POST"])
@admin_required
def edit_user(user_id):
    pass

@app.route("/u/<int:user_id>/permissions", methods=["POST"])
@admin_required
def edit_permissions(user_id):
    pass
