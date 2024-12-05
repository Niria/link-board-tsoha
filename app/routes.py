from sqlalchemy import text

from app import app
from flask import (jsonify, redirect, render_template, request, session,
                   url_for, \
    flash)
from .content import get_category, get_threads, get_thread, \
    get_replies, add_reply, add_thread, toggle_thread_like, \
    toggle_reply_like, get_profile, get_user_replies, toggle_user_follow, \
    get_user_followers, toggle_category_fav, update_thread, update_reply, \
    update_profile
from .db import db
from .users import check_csrf, login_required

from .utils import fetch_thumbnail


@app.route("/")
@login_required
def index():
    threads = get_threads(user_id=session["user_id"])
    return render_template("index.html",
                            category="All",
                            threads=threads)
@app.route("/favourites")
@login_required
def favourites():
    threads = get_threads(user_id=session["user_id"], favourites=True)
    return render_template("index.html", category="Favourites", threads=threads)



@app.route("/c/<string:category>")
@login_required
def category_page(category: str):
    category = get_category(category, session["user_id"])
    if not category or (not category.is_public and session["user_role"] < 1
                        and not category.permission):
        return redirect(url_for("index"))
    threads = get_threads(category_id=category.id, user_id=session["user_id"])
    return render_template("category.html",
                           category=category,
                           threads=threads)


@app.route("/c/<string:category>/favourite", methods=["POST"])
@login_required
def favourite_category(category: str):
    if request.method == "POST":
        check_csrf()
        user_id = session["user_id"]
        favourite = toggle_category_fav(category, user_id)
        return jsonify({"favourite": favourite[0]})

@app.route("/p/<int:thread_id>", methods=["GET", "POST"])
@login_required
def thread_page(thread_id: int):
    if request.method == "GET":
        thread = get_thread(thread_id, session["user_id"])
        if not thread:
            return redirect("/")
        replies = get_replies(thread_id, session["user_id"])
        return render_template("thread.html", thread=thread, replies=replies)
    if request.method == "POST":
        check_csrf()
        user_id = session["user_id"]
        thread_id = request.form["thread_id"]
        parent_id = request.form["parent_id"] or None
        content = request.form["content"]
        if not 1 <= len(content) <= 1000:
            flash("Reply must be between 1 and 1000 characters long.", "error")
            return redirect(url_for("thread_page", thread_id=thread_id))
        add_reply(user_id, thread_id, parent_id, content)
        return redirect(url_for('thread_page', thread_id=thread_id))


@app.route("/c/<string:category>/new", methods=["GET", "POST"])
@login_required
def new_thread(category: str):
    if request.method == "GET":
        return render_template("thread_form.html", category=category,
                               editing=False)
    if request.method == "POST":
        check_csrf()
        category_id = get_category(category, session["user_id"])
        if not category_id:
            flash("Category does not exist.", "error")
            return redirect(url_for("category_page", category=category))
        category_id = category_id[0]
        user_id = session["user_id"]
        link_url = request.form["link_url"]
        redirect_user = False
        if not 3 <= len(link_url) <= 50:
            flash("Link URL must be between 3 and 50 characters long.", "error")
            redirect_user = True
        title = request.form["title"]
        if not 3 <= len(title) <= 50:
            flash("Title must be between 3 and 50 characters long.", "error")
            redirect_user = True
        if redirect_user:
            return redirect(url_for("new_thread", category=category))
        content = request.form["content"]

        thread_thumbnail = None
        if request.form["fetch-img"] == "true":
            thread_thumbnail = fetch_thumbnail(link_url)

        add_thread(user_id, category_id, link_url, title, content, thread_thumbnail)
        return redirect(url_for("category_page", category=category))


@app.route("/p/<int:thread_id>/edit", methods=["GET", "POST"])
def edit_thread(thread_id):
    thread = get_thread(thread_id, session["user_id"])
    if session["user_id"] != thread.user_id and session["user_role"] < 1:
        return render_template("error.html",
                               message="You are not authorised to edit this "
                                       "thread.")
    if request.method == "GET":
        return render_template("thread_form.html", editing=True, thread=thread)
    if request.method == "POST":
        check_csrf()
        link_url = request.form["link_url"]
        redirect_user = False
        if not 3 <= len(link_url) <= 50:
            flash("Link URL must be between 3 and 50 characters.", "error")
            redirect_user = True
        title = request.form["title"]
        if not 3 <= len(title) <= 50:
            flash("Title must be between 3 and 50 characters.", "error")
            redirect_user = True
        if redirect_user:
            return redirect(url_for("edit_thread", thread_id=thread.id))
        content = request.form["content"]
        visible = None
        if 'visible' in request.form:
            visible = True if request.form["visible"] == "true" else False
        thread_thumbnail = None
        update_thumbnail = False
        if request.form["fetch-img"] == "true":
            thread_thumbnail = fetch_thumbnail(link_url)
            update_thumbnail = True
        elif request.form["fetch-img"] == "delete":
            update_thumbnail = True
        update_thread(thread_id, link_url, title, content, visible, thread_thumbnail, update_thumbnail)

        return redirect(url_for("thread_page", thread_id=thread_id))


@app.route("/p/<int:thread_id>/like", methods=["POST"])
@login_required
def like_thread(thread_id: int):
    if request.method == "POST":
        check_csrf()
        user_id = session["user_id"]
        like_count = toggle_thread_like(user_id, thread_id)
        return jsonify({"likes":like_count[0]})


@app.route("/p/<int:thread_id>/<int:reply_id>/like", methods=["POST"])
@login_required
def like_reply(thread_id: int, reply_id: int):
    if request.method == "POST":
        check_csrf()
        user_id = session["user_id"]
        like_count = toggle_reply_like(user_id, reply_id)
        return jsonify({"likes":like_count[0]})


@app.route("/p/<int:thread_id>/<int:reply_id>/edit", methods=["POST"])
def edit_reply(thread_id, reply_id):
    if request.method == "POST":
        check_csrf()
        reply = db.session.execute(text("""SELECT user_id 
                                             FROM replies 
                                            WHERE id=:reply_id"""),
                                   {"reply_id": reply_id}).fetchone()
        if session["user_id"] != reply.user_id and session["user_role"] < 1:
            flash("You are not authorised to edit this reply.", "error")
            return redirect(url_for("thread_page", thread_id=thread_id))
        content = request.form["content"]
        visible = None
        if 'visible' in request.form:
            visible = True if request.form["visible"] == "true" else False
        if not 1 <= len(content) <= 1000:
            flash("Reply content must be between 1 and 1000 characters.",
                  "error")
            return redirect(url_for("thread_page", thread_id=thread_id))
        update_reply(reply_id, content, visible)
        return redirect(url_for('thread_page', thread_id=thread_id))


@app.route("/u/<string:username>/<string:page>")
@app.route("/u/<string:username>")
@login_required
def profile(username: str, page=None):
    user = get_profile(username, session["user_id"])
    if page == "threads":
        user_threads = get_threads(by_user=user.id)
        return render_template("user_profile.html", page=page,
                               user=user, threads=user_threads)
    elif page == "replies":
        user_replies = get_user_replies(user_id=user.id,
                                        session_user=session["user_id"])
        return render_template("user_profile.html", page=page,
                               user=user, replies=user_replies)
    elif page == "followers":
        followers = get_user_followers(user_id=user.id)
        return render_template("user_profile.html", page=page,
                               user=user, followers=followers)
    return render_template("user_profile.html", user=user)


@app.route("/u/<string:username>/edit", methods=["GET", "POST"])
@login_required
def edit_profile(username: str):
    if request.method == "GET":
        user = get_profile(username, session["user_id"])
        if user.id != session["user_id"] and session["user_role"] < 1:
            flash("You are not authorised to edit this profile.", "error")
            return redirect(url_for("profile", username=username))
        return render_template("user_profile_form.html", user=user)

    if request.method == "POST":
        user = get_profile(username, session["user_id"])
        if user.id != session["user_id"] and session["user_role"] < 1:
            flash("You are not authorised to edit this profile.", "error")
            return redirect(url_for("profile", username=username))
        display_name = request.form.get("display_name")
        if 3 > len(display_name) > 20:
            flash("Display name must be between 3 and 20 characters.", "error")
            return redirect(url_for("edit_profile", username=username))
        description = request.form.get("description")
        public_toggle = request.form.get("is_public")
        is_public = None
        if public_toggle:
            is_public = True if public_toggle == "true" else False
        update_profile(user.id, display_name, description, is_public)
        return redirect(url_for("profile", username=username))

@app.route("/u/<string:username>/follow", methods=["POST"])
@login_required
def follow(username: str):
    if request.method == "POST":
        check_csrf()
        following = toggle_user_follow(username, session["user_id"])
        return jsonify({"following": following[0]})


# Catches invalid paths
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template("error.html",
                           message="Nothing to be found here")
