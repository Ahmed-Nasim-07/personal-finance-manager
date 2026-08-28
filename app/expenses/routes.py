from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.auth.utils import login_required
from app.extensions import db
from app.models.expense import Expense
from app.models.category import Category


expenses = Blueprint(
    "expenses",
    __name__,
    url_prefix="/expenses",
)


@expenses.route("/")
@login_required
def list_expenses():
    expenses_list = Expense.query.filter_by(
        user_id=session["user_id"]
    ).order_by(Expense.date.desc()).all()

    return render_template(
        "expenses/list.html",
        expenses=expenses_list,
    )

@expenses.route("/add", methods=["GET", "POST"])
@login_required
def add_expense():

    categories = Category.query.filter_by(
        user_id=session["user_id"],
        type="expense"
    ).order_by(Category.name.asc()).all()

    if request.method == "POST":
        amount = request.form.get("amount")
        description = request.form.get("description")
        expense_date = request.form.get("date")
        category_id = request.form.get("category_id")

        if not amount:
            flash("Amount is required.", "error")
            return render_template(
                "expenses/add.html",
                categories=categories
            )

        try:
            amount = Decimal(amount)
        except InvalidOperation:
            flash("Please enter a valid amount.", "error")
            return render_template(
                "expenses/add.html",
                categories=categories
            )

        if amount <= 0:
            flash("Amount must be greater than zero.", "error")
            return render_template(
                "expenses/add.html",
                categories=categories
            )

        category = Category.query.filter_by(
            id=category_id,
            user_id=session["user_id"],
            type="expense"
        ).first()

        if not category:
            flash("Invalid category.", "error")
            return render_template(
                "expenses/add.html",
                categories=categories
            )

        try:
            expense_date = date.fromisoformat(expense_date)
        except (ValueError, TypeError):
            flash("Please enter a valid date.", "error")
            return render_template(
                "expenses/add.html",
                categories=categories
            )

        expense = Expense(
            user_id=session["user_id"],
            amount=amount,
            description=description,
            date=expense_date,
            category_id=category.id,
        )

        db.session.add(expense)
        db.session.commit()

        return redirect(url_for("expenses.list_expenses"))

    return render_template(
        "expenses/add.html",
        categories=categories
    )

@expenses.route("/<int:expense_id>/edit", methods=["GET", "POST"])
@login_required
def edit_expense(expense_id):
    expense = Expense.query.filter_by(
        id=expense_id,
        user_id=session["user_id"]
    ).first_or_404()

    categories = Category.query.filter_by(
        user_id=session["user_id"],
        type="expense"
    ).order_by(Category.name.asc()).all()

    if request.method == "POST":
        amount = request.form.get("amount")
        description = request.form.get("description")
        expense_date = request.form.get("date")
        category_id = request.form.get("category_id")

        if not amount:
            flash("Amount is required.", "error")
            return render_template(
                "expenses/edit.html",
                expense=expense,
                categories=categories
            )

        try:
            amount = Decimal(amount)
        except InvalidOperation:
            flash("Please enter a valid amount.", "error")
            return render_template(
                "expenses/edit.html",
                expense=expense,
                categories=categories
            )

        if amount <= 0:
            flash("Amount must be greater than zero.", "error")
            return render_template(
                "expenses/edit.html",
                expense=expense,
                categories=categories
            )

        category = Category.query.filter_by(
            id=category_id,
            user_id=session["user_id"],
            type="expense"
        ).first()

        if not category:
            flash("Invalid category.", "error")
            return render_template(
                "expenses/edit.html",
                expense=expense,
                categories=categories
            )

        try:
            expense_date = date.fromisoformat(expense_date)
        except (ValueError, TypeError):
            flash("Please enter a valid date.", "error")
            return render_template(
                "expenses/edit.html",
                expense=expense,
                categories=categories
            )

        expense.amount = amount
        expense.description = description
        expense.date = expense_date
        expense.category_id = category.id

        db.session.commit()

        return redirect(url_for("expenses.list_expenses"))

    return render_template(
        "expenses/edit.html",
        expense=expense,
        categories=categories
    )

@expenses.route("/<int:expense_id>/delete", methods=["POST"])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.filter_by(
        id=expense_id,
        user_id=session["user_id"]
    ).first_or_404()

    db.session.delete(expense)
    db.session.commit()

    flash("Expense deleted successfully.", "success")

    return redirect(url_for("expenses.list_expenses"))