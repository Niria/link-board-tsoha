from app import app
from flask import jsonify, redirect, render_template, request, session, url_for
from .content import get_category_id, get_threads, get_thread, \
    get_replies, add_reply, add_thread, toggle_thread_like, \
    toggle_reply_like
from .utils import login_required
from . import users


@app.route("/")
@login_required
def index():
    threads = get_threads(None)
    if not threads:
        return render_template("error.html", message="Invalid category")
    return render_template("index.html", 
                            category="all", 
                            threads=threads)

@app.route("/c/<string:category>")
@login_required
def category_page(category: str):
    threads = get_threads(category)
    if not threads:
        return redirect("/")
    return render_template("category.html", 
                           category=category, 
                           threads=threads)

@app.route("/p/<int:thread_id>", methods=["GET", "POST"])
@login_required
def thread_page(thread_id: int):
    if request.method == "GET":
        thread = get_thread(thread_id, session["user_id"])
        if not thread:
            return redirect("/")
        replies = get_replies(thread_id, session["user_id"])
        for r in replies:
            print(r._mapping)
        return render_template("thread.html", thread=thread, replies=replies)
    if request.method == "POST":
        users.check_csrf()
        print("hello", request.headers)
        user_id = session["user_id"]
        thread_id = request.form["thread_id"]
        parent_id = request.form["parent_id"] or None
        content = request.form["content"]

        add_reply(user_id, thread_id, parent_id, content)
        return redirect(url_for('thread_page', thread_id=thread_id))

@app.route("/c/<string:category>/new", methods=["GET", "POST"])
@login_required
def new_thread(category: str):
    if request.method == "GET":
        return render_template("new_thread.html", category=category)
    if request.method == "POST":
        users.check_csrf()
        category_id = get_category_id(category)
        if not category_id:
            return render_template("error.html", message="Category does not exist")
        category_id = category_id[0]
        user_id = session["user_id"]
        link_url = request.form["link_url"]
        title = request.form["title"]
        content = request.form["content"]

        add_thread(user_id, category_id, link_url, title, content)
        return redirect("/")

@app.route("/p/<int:thread_id>/like", methods=["POST"])
@login_required
def like_thread(thread_id: int):
    if request.method == "POST":
        users.check_csrf()
        user_id = session["user_id"]
        like_count = toggle_thread_like(user_id, thread_id)
        return jsonify({"likes":like_count[0]})

@app.route("/p/<int:thread_id>/<int:reply_id>/like", methods=["POST"])
@login_required
def like_reply(thread_id: int, reply_id: int):
    if request.method == "POST":
        users.check_csrf()
        user_id = session["user_id"]
        like_count = toggle_reply_like(user_id, reply_id)
        return jsonify({"likes":like_count[0]})

# Catches invalid paths
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template("error.html", message="Nothing to be found here")

