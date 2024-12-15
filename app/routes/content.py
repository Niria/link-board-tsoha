from sqlalchemy import text

from app.services import categories as category_service
from app.services import search as search_service
from app.services import threads as thread_service
from app.services import users as user_service

from app import app
from flask import (jsonify, redirect, render_template, request, session,
                   url_for, flash, abort)
from app.utils.db import db
from app.utils.forms import (EditUserProfileForm, EditReplyForm, EditThreadForm,
                             AdminEditThreadForm, NewThreadForm, AdminEditReplyForm,
                             NewReplyForm, SearchForm)
from app.utils.decorators import login_required
from app.utils.thumbnail import fetch_thumbnail


@app.route("/")
@login_required
def index():
    threads = thread_service.get_threads(user_id=session["user_id"])
    return render_template("index.html",
                           category="All",
                           threads=threads)


@app.route("/favourites")
@login_required
def favourites():
    threads = thread_service.get_threads(user_id=session["user_id"], favourites=True)
    return render_template("index.html", category="Favourites", threads=threads)


@app.route("/c/<string:category>")
@login_required
def category_page(category: str):
    category = category_service.get_category(category, session["user_id"])
    if not category or (not category.is_public and session["user_role"] < 1
                        and not category.permission):
        flash("Category does not exist or is set to private.", "error")
        return redirect(url_for("index"))
    threads = thread_service.get_threads(category_id=category.id, user_id=session["user_id"])
    return render_template("category.html",
                           category=category,
                           threads=threads)


@app.route("/c/<string:category>/favourite", methods=["POST"])
@login_required
def favourite_category(category: str):
    if request.method == "POST":
        user_id = session["user_id"]
        try:
            favourite = category_service.toggle_category_fav(category, user_id)
            return jsonify({"success": True, "favourite": favourite[0]})
        except ValueError as e:
            flash(str(e), "error")
            return jsonify({"success": False})

@app.route("/p/<int:thread_id>", methods=["GET", "POST"])
@login_required
def thread_page(thread_id: int):
    thread = thread_service.get_thread(thread_id, session["user_id"])
    if not thread:
        flash("Thread does not exist", "error")
        return redirect("/")
    if request.method == "GET":
        replies = thread_service.get_replies(thread_id, session["user_id"])
        return render_template("thread.html", thread=thread, replies=replies)
    if request.method == "POST":
        form = NewReplyForm(request.form)
        form.parent_id.data = request.form.get("parent_id")
        if form.parent_id.data == "":
            form.parent_id.data = None
        form.message.data = request.form.get("content").strip()
        if form.validate_on_submit():
            user_id = session["user_id"]
            thread_service.add_reply(user_id, thread.id, form.parent_id.data, form.message.data)
            flash(f"Reply added to thread '{thread.title}'", "success")
        else:
            for field, error in form.errors.items():
                flash(error[0], "error")
        return redirect(url_for('thread_page', thread_id=thread_id))


@app.route("/c/<string:category>/new", methods=["GET", "POST"])
@login_required
def new_thread(category: str):
    form = NewThreadForm()
    if form.validate_on_submit():
        category = category_service.get_category(category, session["user_id"])
        if not category:
            flash("Category does not exist.", "error")
            return redirect(url_for("category_page", category=category))
        thumbnail = None
        url = form.url.data.strip("/")
        if form.fetch_image.data:
            thumbnail = fetch_thumbnail(url)
        thread_service.add_thread(session["user_id"], category.id, url, form.title.data.strip(), form.message.data, thumbnail)
        flash(f"New thread created: '{form.title.data.strip()}'", "success")
        return redirect(url_for("category_page", category=category.name))
    return render_template("thread_form.html", category=category,
                           editing=False, form=form)


@app.route("/p/<int:thread_id>/edit", methods=["GET", "POST"])
@login_required
def edit_thread(thread_id):
    thread = thread_service.get_thread(thread_id, session["user_id"])
    if not thread:
        flash("Invalid thread", "error")
        return redirect(url_for("index"))
    if session["user_role"] > 0:
        form = AdminEditThreadForm()
    elif session["user_id"] == thread.user_id:
        form = EditThreadForm()
    else:
        return render_template("error.html",
                               message="You are not authorised to edit this thread.")
    if form.validate_on_submit():
        update_thumbnail = False
        thread_thumbnail = None
        url = form.url.data.strip("/")
        if form.refresh_image.data == "refresh":
            thread_thumbnail = fetch_thumbnail(url)
            update_thumbnail = True
        elif form.refresh_image.data == "delete":
            update_thumbnail = True
        visible = None
        if session["user_role"] > 0:
            visible = form.visible.data
        try:
            thread_service.update_thread(thread.id, url, form.title.data, form.message.data, visible, thread_thumbnail, update_thumbnail)
            flash(f"Edited thread: '{form.title.data.strip()}'", "success")
            return redirect(url_for("thread_page", thread_id=thread.id))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("thread_form.html", editing=True,
                                   thread=thread, form=form)
    elif request.method == "GET":
        if session["user_role"] > 0:
            form.visible.data = thread.visible
        form.url.data = thread.link_url
        form.title.data = thread.title
        form.message.data = thread.content
        form.refresh_image.data = "keep"
    return render_template("thread_form.html", editing=True, thread=thread, form=form)


@app.route("/p/<int:thread_id>/like", methods=["POST"])
@login_required
def like_thread(thread_id: int):
    if request.method == "POST":
        user_id = session["user_id"]
        like_count = thread_service.toggle_thread_like(user_id, thread_id)
        return jsonify({"likes":like_count[0]})


@app.route("/p/<int:thread_id>/<int:reply_id>/like", methods=["POST"])
@login_required
def like_reply(thread_id: int, reply_id: int):
    if request.method == "POST":
        user_id = session["user_id"]
        like_count = thread_service.toggle_reply_like(user_id, reply_id)
        return jsonify({"likes":like_count[0]})


@app.route("/p/<int:thread_id>/<int:reply_id>/edit", methods=["POST"])
@login_required
def edit_reply(thread_id, reply_id):
    if request.method == "POST":
        reply = db.session.execute(text("""SELECT id, user_id, visible
                                             FROM replies 
                                            WHERE id=:reply_id"""),
                                   {"reply_id": reply_id}).fetchone()
        if not reply:
            flash("Invalid reply", "error")
            return redirect(url_for("thread_page", thread_id=thread_id))
        if session["user_id"] != reply.user_id and session["user_role"] < 1:
            flash("You are not authorised to edit this reply.", "error")
            return redirect(url_for("thread_page", thread_id=thread_id))

        content = request.form.get("content")
        if content:
            content = content.strip()
        visible = None
        if "visible" in request.form:
            visible = True if request.form["visible"] == "true" else False
        if session["user_role"] > 0:
            form = AdminEditReplyForm()
            form.visible.data = visible
        else:
            form = EditReplyForm()
        form.message.data = content
        if form.validate_on_submit():
            visible = None
            if session["user_role"] > 0:
                visible = form.visible.data
            try:
                thread_service.update_reply(reply.id, form.message.data, visible)
                flash("Reply updated", "success")
            except ValueError as e:
                flash(str(e), "error")
        else:
            for field, error in form.errors.items():
                flash(error[0], "error")
        return redirect(url_for("thread_page", thread_id=thread_id))


@app.route("/u/<string:username>/<string:page>")
@app.route("/u/<string:username>")
@login_required
def profile(username: str, page=None):
    user = user_service.get_profile(username, session["user_id"])
    if not user:
        flash("User not found", "error")
        return redirect(url_for("index"))
    if page == "threads":
        user_threads = thread_service.get_threads(by_user=user.id)
        return render_template("user_profile.html", page=page,
                               user=user, threads=user_threads)
    elif page == "replies":
        user_replies = user_service.get_user_replies(user_id=user.id,
                                        session_user=session["user_id"])
        return render_template("user_profile.html", page=page,
                               user=user, replies=user_replies)
    elif page == "followers":
        followers = user_service.get_user_followers(user_id=user.id)
        return render_template("user_profile.html", page=page,
                               user=user, followers=followers)
    return render_template("user_profile.html", user=user)


@app.route("/u/<string:username>/edit", methods=["GET", "POST"])
@login_required
def edit_profile(username: str):
    form = EditUserProfileForm()
    user = user_service.get_profile(username, session["user_id"])
    if not user:
        flash("Invalid user.", "error")
        return redirect(url_for("index"))
    if user.id != session["user_id"] and session["user_role"] < 1:
        flash("You are not authorised to edit this profile.", "error")
        return redirect(url_for("profile", username=username))
    if form.validate_on_submit():
        user_service.update_profile(user.id, form.display_name.data, form.description.data, form.is_public.data)
        flash(f"Profile updated", "success")
        return redirect(url_for("profile", username=username))
    elif request.method == "GET":
        form.display_name.data = user.display_name
        form.description.data = user.description
        form.is_public.data = user.profile_public
    return render_template("user_profile_form.html", user=user, form=form)


@app.route("/u/<string:username>/follow", methods=["POST"])
@login_required
def follow(username: str):
    if request.method == "POST":
        try:
            following = user_service.toggle_user_follow(username, session["user_id"])
            return jsonify({"success": True, "following":following[0]})
        except ValueError as e:
            flash(str(e), "error")
            return jsonify({"success": False})

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    form = SearchForm()
    form.search_type.choices = [("user", "Users"),
                                ("category", "Categories"),
                                ("thread", "Threads")]


    if form.validate_on_submit():
        results = search_service.keyword_search(form.search_type.data,
                                                     form.search_string.data,
                                                     session["user_id"])
        return render_template("search.html", form=form,
                               type=form.search_type.data, results=results)

    return render_template("search.html", form=form, results=None)


# Catches invalid paths
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
@login_required
def catch_all(path):
    abort(404)
