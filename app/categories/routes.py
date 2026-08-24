from flask import Blueprint, render_template, request, redirect, url_for, session
from app.auth.utils import login_required
from app.extensions import db
from app.models.category import Category


categories = Blueprint(
    "categories",
    __name__,
    url_prefix="/categories",
)

@categories.route("/")
@login_required
def list_categories():
    categories_list = Category.query.filter_by(
        user_id=session["user_id"]
    ).order_by(Category.name.asc()).all()

    return render_template(
        "categories/list.html",
        categories=categories_list,
    )

@categories.route("/add", methods=["GET", "POST"])
@login_required
def add_category():
    if request.method == "POST":
        name = request.form.get("name")
        category_type = request.form.get("type")

        if not name:
            return "Category name is required", 400

        if category_type not in ("income", "expense"):
            return "Invalid category type", 400

        category = Category(
            user_id=session["user_id"],
            name=name,
            type=category_type,
        )

        db.session.add(category)
        db.session.commit()

        return redirect(url_for("categories.list_categories"))

    return render_template("categories/add.html")

@categories.route("/<int:category_id>/edit", methods=["GET", "POST"])
@login_required
def edit_category(category_id):
    category = Category.query.filter_by(
        id=category_id,
        user_id=session["user_id"]
    ).first_or_404()

    if request.method == "POST":
        name = request.form.get("name")
        category_type = request.form.get("type")

        if not name:
            return "Category name is required", 400

        if category_type not in ("income", "expense"):
            return "Invalid category type", 400

        category.name = name
        category.type = category_type

        db.session.commit()

        return redirect(url_for("categories.list_categories"))

    return render_template(
        "categories/edit.html",
        category=category
    )

@categories.route("/<int:category_id>/delete", methods=["POST"])
@login_required
def delete_category(category_id):
    category = Category.query.filter_by(
        id=category_id,
        user_id=session["user_id"]
    ).first_or_404()

    db.session.delete(category)
    db.session.commit()

    return redirect(url_for("categories.list_categories"))