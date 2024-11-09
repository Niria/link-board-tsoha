from app import app
from flask import redirect, render_template, request, session
from .content import add_reply, get_category_threads, get_all_threads, get_thread, get_replies


@app.route("/")
def index():
    threads = get_all_threads()
    return render_template("index.html", 
                            category="all", 
                            threads=threads)


@app.route("/c/<string:category>")
def category_page(category: str):
    threads = get_category_threads(category)
    return render_template("category.html", 
                           category=category, 
                           threads=threads)

@app.route("/p/<int:thread_id>", methods=["GET", "POST"])
def thread_page(thread_id: int):
    if request.method == "GET":
        thread = get_thread(thread_id)
        replies = get_replies(thread_id)
        return render_template("thread.html", thread=thread, replies=replies)
    elif request.method == "POST":
        user_id = session["user_id"]
        thread_id = request.form["thread_id"]
        parent_id = request.form["parent_id"] or None
        content = request.form["content"]

        add_reply(user_id, thread_id, parent_id, content)
        return redirect(f"/p/{thread_id}")