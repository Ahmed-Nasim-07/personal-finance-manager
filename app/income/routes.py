from datetime import date

from flask import Blueprint, render_template, request, redirect, url_for, session

from app.auth.utils import login_required
from app.extensions import db
from app.models.income import Income
from app.models.category import Category


income_bp = Blueprint(
    "income",
    __name__,
    url_prefix="/income",
)


@income_bp.route("/")
@login_required
def list_income():
    income_list = Income.query.filter_by(
        user_id=session["user_id"]
    ).order_by(Income.date.desc()).all()

    return render_template(
        "income/list.html",
        income=income_list,
    )


@income_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_income():
    if request.method == "POST":
        amount = request.form.get("amount")
        description = request.form.get("description")
        income_date = request.form.get("date")
        category_id = request.form.get("category_id")

        if not amount or not income_date or not category_id:
            return "Amount, date and category are required", 400

        category = Category.query.filter_by(
            id=category_id,
            user_id=session["user_id"],
            type="income"
        ).first()

        if not category:
            return "Invalid category", 400

        income = Income(
            user_id=session["user_id"],
            amount=amount,
            description=description,
            date=date.fromisoformat(income_date),
            category_id=category.id,
        )

        db.session.add(income)
        db.session.commit()

        return redirect(url_for("income.list_income"))

    categories = Category.query.filter_by(
        user_id=session["user_id"],
        type="income"
    ).order_by(Category.name.asc()).all()

    return render_template(
        "income/add.html",
        categories=categories
    )


@income_bp.route("/<int:income_id>/edit", methods=["GET", "POST"])
@login_required
def edit_income(income_id):
    income = Income.query.filter_by(
        id=income_id,
        user_id=session["user_id"]
    ).first_or_404()

    if request.method == "POST":
        amount = request.form.get("amount")
        description = request.form.get("description")
        income_date = request.form.get("date")
        category_id = request.form.get("category_id")

        if not amount or not income_date or not category_id:
            return "Amount, date and category are required", 400

        category = Category.query.filter_by(
            id=category_id,
            user_id=session["user_id"],
            type="income"
        ).first()

        if not category:
            return "Invalid category", 400

        income.amount = amount
        income.description = description
        income.date = date.fromisoformat(income_date)
        income.category_id = category.id

        db.session.commit()

        return redirect(url_for("income.list_income"))

    categories = Category.query.filter_by(
        user_id=session["user_id"],
        type="income"
    ).order_by(Category.name.asc()).all()

    return render_template(
        "income/edit.html",
        income=income,
        categories=categories
    )


@income_bp.route("/<int:income_id>/delete", methods=["POST"])
@login_required
def delete_income(income_id):
    income = Income.query.filter_by(
        id=income_id,
        user_id=session["user_id"]
    ).first_or_404()

    db.session.delete(income)
    db.session.commit()

    return redirect(url_for("income.list_income"))