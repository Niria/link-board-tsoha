from flask import render_template, redirect, request, session, url_for, flash

from app import app
from .content import (create_category, get_category, update_category,
                      users_without_permissions, users_with_permissions,
                      toggle_permissions)
from .forms import AddPermissionsForm, RemovePermissionsForm, EditCategoryForm, \
    NewCategoryForm
from .users import admin_required, login_required


@app.route("/new_category", methods=["GET", "POST"])
@login_required
@admin_required
def new_category():
    form = NewCategoryForm()
    if form.validate_on_submit():
        try:
            create_category(form.name.data, form.description.data, form.is_public.data)
            flash(f"Category '{form.name.data}' created successfully!", "success")
            return redirect(url_for("category_page", category=form.name.data))
        except ValueError as e:
            flash(str(e), "error")
    return render_template("category_form.html", form=form)


@app.route("/c/<string:category>/edit", methods=["GET", "POST"])
@login_required
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
        flash(f"Category '{form.name.data}' updated successfully!", "success")
        return redirect(url_for("category_page", category=form.name.data))
    if request.method == "GET":
        form.name.data = category.name
        form.description.data = category.description
        form.is_public.data = category.is_public
    return render_template("category_form.html", category=category, form=form)


@app.route("/c/<string:category>/permissions", methods=["GET", "POST"])
@login_required
@admin_required
def edit_permissions(category: str):
    category = get_category(category, session["user_id"])
    if not category:
        flash("Invalid category.", "error")
        return redirect(url_for("index"))
    add_user_form = AddPermissionsForm()
    remove_user_form = RemovePermissionsForm()
    unapproved_users = users_without_permissions(category.id)
    approved_users = users_with_permissions(category.id)
    add_user_form.user_id.choices = [(u.id, u.username) for u in unapproved_users]

    if request.form.get("submit") == "Add" and add_user_form.validate_on_submit():
        try:
            toggle_permissions(add_user_form.user_id.data, category.name)
            username = dict(add_user_form.user_id.choices).get(add_user_form.user_id.data)
            flash(f"Added permissions for user '{username}' successfully!", "success")
        except ValueError as e:
            flash(str(e), "error")
        return redirect(url_for("edit_permissions", category=category.name))
    elif request.form.get("submit") == "Remove" and remove_user_form.validate_on_submit():
        user_id = request.form.get('user_id', type=int)
        try:
            toggle_permissions(user_id, category.name)
            flash(f"Removed permissions from user '{request.form.get("username")}' successfully!", "success")
        except ValueError as e:
            flash(str(e), "error")
        return redirect(url_for("edit_permissions", category=category.name))

    return render_template("category_permissions.html",
                           category=category,
                           unapproved_users=unapproved_users,
                           approved_users=approved_users,
                           add_form=add_user_form,
                           remove_form=remove_user_form)

