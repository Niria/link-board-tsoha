from app import app
from flask import render_template
from .content import get_categories, get_category, get_threads

@app.route("/")
def index():
    categories = get_categories()
    threads = get_threads()
    return render_template("index.html", categories=categories, threads=threads)


@app.route("/c/<string:category>")
def category_page(category: str):
    category = get_category(category)
    return render_template("category.html", category=category)