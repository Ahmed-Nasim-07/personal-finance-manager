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

    search = request.args.get("search", "").strip()
    category_id = request.args.get("category_id")
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    min_amount = request.args.get("min_amount") or None
    max_amount = request.args.get("max_amount") or None

    filters_applied = any([
        search,
        category_id,
        from_date,
        to_date,
        min_amount,
        max_amount
    ])

    query = Expense.query.filter_by(
        user_id=session["user_id"]
    )

    if search:
        query = query.filter(
            Expense.description.ilike(f"%{search}%")
        )

    if category_id:
        query = query.filter(
            Expense.category_id == category_id
        )

    if from_date:
        try:
            from_date = date.fromisoformat(from_date)
            query = query.filter(
                Expense.date >= from_date
            )
        except ValueError:
            flash("Invalid starting date.", "error")

    if to_date:
        try:
            to_date = date.fromisoformat(to_date)
            query = query.filter(
                Expense.date <= to_date
            )
        except ValueError:
            flash("Invalid ending date.", "error")

    if min_amount:
        try:
            min_amount = Decimal(min_amount)
        except InvalidOperation:
            flash("Invalid minimum amount.", "error")
            min_amount = None

    if max_amount:
        try:
            max_amount = Decimal(max_amount)
        except InvalidOperation:
            flash("Invalid maximum amount.", "error")
            max_amount = None

    if (
        min_amount is not None
        and max_amount is not None
        and min_amount > max_amount
    ):
        flash(
            "Minimum amount cannot be greater than maximum amount.",
            "error"
        )
    else:
        if min_amount is not None:
            query = query.filter(
                Expense.amount >= min_amount
            )

        if max_amount is not None:
            query = query.filter(
                Expense.amount <= max_amount
            )

    expenses_list = query.order_by(
        Expense.date.desc()
    ).all()

    categories = Category.query.filter_by(
        user_id=session["user_id"],
        type="expense"
    ).order_by(
        Category.name.asc()
    ).all()

    return render_template(
        "expenses/list.html",
        expenses=expenses_list,
        categories=categories,
        filters_applied=filters_applied
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