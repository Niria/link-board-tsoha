from flask import render_template, redirect, request, session, url_for, flash

from app import app
from .content import (create_category, get_category, update_category,
                      users_without_permissions, users_with_permissions,
                      toggle_permissions)
from .users import admin_required, check_csrf


@app.route("/new_category", methods=["GET", "POST"])
@admin_required
def new_category():
    if request.method == "GET":
        return render_template("category_form.html")
    if request.method == "POST":
        print(request.form.get('csrf_token'))
        check_csrf()
        category_name = request.form["category_name"]
        if len(category_name) < 3:
            flash("Category name must be at least 3 characters.", "error")
            return redirect(url_for("new_category"))
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
            flash("Category name must be at least 3 characters.", "error")
            return redirect(url_for("new_category"))
        description = request.form["description"]
        public = True if request.form["public"] == "true" else False
        update_category(category, new_category_name, description, public)
        return redirect(url_for("category_page", category=new_category_name))


@app.route("/u/<int:user_id>/edit", methods=["POST"])
@admin_required
def edit_user(user_id):
    pass


@app.route("/c/<string:category>/permissions", methods=["GET", "POST"])
@admin_required
def edit_permissions(category: str):
    if request.method == "GET":
        category = get_category(category, session["user_id"])
        if not category:
            flash("Invalid category.", "error")
            return redirect(url_for("edit_permissions", category=category))
        unapproved_users = users_without_permissions(category.id)
        approved_users = users_with_permissions(category.id)
        return render_template("category_permissions.html", category=category,
                               unapproved_users=unapproved_users,
                               approved_users=approved_users)

    if request.method == "POST":
        check_csrf()
        user_id = request.form.get('user_id', type=int)
        toggle_permissions(user_id, category)
        return redirect(request.url)
