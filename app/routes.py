from app import app
from flask import render_template
from .content import get_category_threads, get_all_threads, get_thread, get_replies


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

@app.route("/p/<int:thread_id>")
def thread_page(thread_id: int):
    thread = get_thread(thread_id)
    replies = get_replies(thread_id)
    return render_template("thread.html", thread=thread, replies=replies)