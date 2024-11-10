from app import app
from flask import redirect, render_template, request, session
from .content import add_reply, get_threads, \
    get_thread, get_replies
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
        thread = get_thread(thread_id)
        if not thread:
            return redirect("/")
        replies = get_replies(thread_id)
        return render_template("thread.html", thread=thread, replies=replies)
    elif request.method == "POST":
        users.check_csrf()
        user_id = session["user_id"]
        thread_id = request.form["thread_id"]
        parent_id = request.form["parent_id"] or None
        content = request.form["content"]

        add_reply(user_id, thread_id, parent_id, content)
        return redirect(f"/p/{thread_id}")

@app.route("/c/<string:category>/new", methods=["GET", "POST"])
@login_required
def new_thread(category: str):
    if request.method == "GET":
        return render_template("new_thread.html")

# Catches invalid paths
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template("error.html", message='Nothing to be found here')

