from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.auth.utils import login_required
from app.extensions import db
from app.models.category import Category
from app.models.expense import Expense
from app.models.income import Income


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
            flash("Category name is required.", "error")
            return render_template("categories/add.html")

        name = name.strip()
        if not name:
            flash("Category name is required.", "error")
            return render_template("categories/add.html")

        if category_type not in ("income", "expense"):
            flash("Invalid category type.", "error")
            return render_template("categories/add.html")

        existing_category = Category.query.filter_by(
            user_id=session["user_id"],
            name=name
        ).first()

        if existing_category:
            flash("A category with this name already exists.", "error")
            return render_template("categories/add.html")

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
            flash("Category name is required.", "error")
            return render_template(
                "categories/edit.html",
                category=category
            )

        name = name.strip()

        if not name:
            flash("Category name is required.", "error")
            return render_template(
                "categories/edit.html",
                category=category
            )

        if category_type not in ("income", "expense"):
            flash("Invalid category type.", "error")
            return render_template(
                "categories/edit.html",
                category=category
            )

        existing_category = Category.query.filter(
            Category.user_id == session["user_id"],
            Category.name == name,
            Category.id != category.id
        ).first()

        if existing_category:
            flash("A category with this name already exists.", "error")
            return render_template(
                "categories/edit.html",
                category=category
            )

        if category_type != category.type:

            expense_exists = Expense.query.filter_by(
                category_id=category.id
            ).first()

            income_exists = Income.query.filter_by(
                category_id=category.id
            ).first()

            if expense_exists or income_exists:
                flash(
                    "You cannot change the type of a category that is already being used.",
                    "error"
                )

                return render_template(
                    "categories/edit.html",
                    category=category
                )

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

    expense_exists = Expense.query.filter_by(
        category_id=category.id
    ).first()

    if expense_exists:
        flash(
            "This category cannot be deleted because it is being used by an expense.",
            "error"
        )
        return redirect(url_for("categories.list_categories"))

    income_exists = Income.query.filter_by(
        category_id=category.id
    ).first()

    if income_exists:
        flash(
            "This category cannot be deleted because it is being used by an income.",
            "error"
        )
        return redirect(url_for("categories.list_categories"))

    db.session.delete(category)
    db.session.commit()

    return redirect(url_for("categories.list_categories"))