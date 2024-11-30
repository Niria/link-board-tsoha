from app import app
from flask import render_template, redirect, request, session, url_for
from sqlalchemy.sql import text

from .content import create_category, get_category, update_category, get_thread, update_thread, update_reply
from .db import db

from .users import admin_required, check_csrf


@app.route("/new_category", methods=["GET", "POST"])
@admin_required
def new_category():
    if request.method == "GET":
        return render_template("category_form.html")
    if request.method == "POST":
        check_csrf()
        category_name = request.form["category_name"]
        if len(category_name) < 3:
            return render_template("error.html", message="Category name must be 3 characters or longer.")
        description = request.form["description"]
        public = True if request.form["public"] == "true" else False
        create_category(category_name, description, public)
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
        if len(new_category_name) < 3:
            return render_template("error.html", message="Category name must be 3 characters or longer.")
        description = request.form["description"]
        public = True if request.form["public"] == "true" else False
        update_category(category, new_category_name, description, public)
        return redirect(url_for("index"))


@app.route("/p/<int:thread_id>/edit", methods=["GET", "POST"])
def edit_thread(thread_id):
    thread = get_thread(thread_id, session["user_id"])
    if session["user_id"] != thread.user_id and session["user_role"] < 1:
        return render_template("error.html", message="You are not authorized to edit this thread.")
    if request.method == "GET":
        return render_template("thread_form.html", editing=True, thread=thread)
    if request.method == "POST":
        check_csrf()
        link_url = request.form["link_url"]
        if not 3 <= len(link_url) <= 50:
            return render_template("error.html", message="Url must be between 3 and 50 characters long.")
        title = request.form["title"]
        if not 3 <= len(title) <= 50:
            return render_template("error.html", message="Title must be between 3 and 50 characters long.")
        content = request.form["content"]
        visible = None
        if 'visible' in request.form:
            visible = True if request.form["visible"] == "true" else False
        update_thread(thread_id, link_url, title, content, visible)

        return redirect("/")



@app.route("/p/<int:thread_id>/<int:reply_id>/edit", methods=["POST"])
def edit_reply(thread_id, reply_id):
    if request.method == "POST":
        check_csrf()
        reply = db.session.execute(text("""SELECT user_id 
                                             FROM replies 
                                            WHERE id=:reply_id"""),
                                   {"reply_id": reply_id}).fetchone()
        if session["user_id"] != reply.user_id and session["user_role"] < 1:
            return render_template("error.html", message="Invalid user.")
        content = request.form["content"]
        visible = None
        if 'visible' in request.form:
            visible = True if request.form["visible"] == "true" else False
        print(visible)
        if not 1 <= len(content) <= 1000:
            return render_template("error.html", message="Reply must be between 1 and 1000 characters long.")
        update_reply(reply_id, content, visible)
        return redirect(url_for('thread_page', thread_id=thread_id))


@app.route("/u/<int:user_id>/edit", methods=["POST"])
@admin_required
def edit_user(user_id):
    pass

@app.route("/u/<int:user_id>/permissions", methods=["POST"])
@admin_required
def edit_permissions(user_id):
    pass
