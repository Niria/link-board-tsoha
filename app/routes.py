from app import app
from flask import render_template
from .content import get_category_list, get_category_threads, \
    get_all_threads, get_thread

@app.route("/")
def index():
    categories = get_category_list()
    threads = get_all_threads()
    return render_template("index.html",
                            categories=categories, 
                            category="all", 
                            threads=threads)


@app.route("/c/<string:category>")
def category_page(category: str):
    categories = get_category_list()
    threads = get_category_threads(category)
    return render_template("category.html", 
                           categories=categories, 
                           category=category, 
                           threads=threads)

@app.route("/p/<int:thread_id>")
def thread_page(thread_id: int):
    thread = get_thread(thread_id)
    return render_template("thread.html", thread=thread)