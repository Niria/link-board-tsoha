from flask import render_template, redirect, request, session, url_for, flash

from app import app
from .content import (create_category, get_category, update_category,
                      users_without_permissions, users_with_permissions,
                      toggle_permissions)
from .forms import AddPermissionsForm, RemovePermissionsForm, EditCategoryForm, \
    NewCategoryForm
from .users import admin_required


@app.route("/new_category", methods=["GET", "POST"])
@admin_required
def new_category():
    form = NewCategoryForm()
    if form.validate_on_submit():
        create_category(form.name.data, form.description.data, form.is_public.data)
        return redirect(url_for("category_page", category=form.name.data))
    return render_template("category_form.html", form=form)


@app.route("/c/<string:category>/edit", methods=["GET", "POST"])
@admin_required
def edit_category(category):
    form = EditCategoryForm()
    category = get_category(category, session["user_id"])
    if not category:
        flash("Category does not exist.", "error")
        return redirect(url_for("index"))
    if form.validate_on_submit():
        update_category(category.id, form.name.data, form.description.data,
                        form.is_public.data)
        return redirect(url_for("category_page", category=form.name.data, form=form))
    if request.method == "GET":
        form.name.data = category.name
        form.description.data = category.description
        form.is_public.data = category.is_public
    return render_template("category_form.html", category=category, form=form)

@app.route("/u/<int:user_id>/edit", methods=["POST"])
@admin_required
def edit_user(user_id):
    pass


@app.route("/c/<string:category>/permissions", methods=["GET", "POST"])
@admin_required
def edit_permissions(category: str):
    category = get_category(category, session["user_id"])
    if not category:
        flash("Invalid category.", "error")
        return redirect(url_for("index"))
    add_user_form = AddPermissionsForm()
    remove_user_form = RemovePermissionsForm()

    if remove_user_form.validate_on_submit():
        user_id = request.form.get('user_id', type=int)
        toggle_permissions(user_id, category.name)
        return redirect(url_for("edit_permissions", category=category.name))

    unapproved_users = users_without_permissions(category.id)
    approved_users = users_with_permissions(category.id)
    add_user_form.user_id.choices = [(u.id, u.username) for u in unapproved_users]
    return render_template("category_permissions.html",
                           category=category,
                           unapproved_users=unapproved_users,
                           approved_users=approved_users,
                           add_form=add_user_form,
                           remove_form=remove_user_form)

