from decimal import Decimal, InvalidOperation
from datetime import date

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)

from app.auth.utils import login_required
from app.extensions import db
from app.models.budget import Budget
from app.models.category import Category
from app.models.expense import Expense


budgets = Blueprint(
    "budgets",
    __name__,
    url_prefix="/budgets"
)


@budgets.route("/")
@login_required
def list_budgets():
    user_id = session["user_id"]

    budget_list = Budget.query.filter_by(
        user_id=user_id
    ).order_by(
        Budget.year.desc(),
        Budget.month.desc()
    ).all()

    for budget in budget_list:

        start_date = date(
            budget.year,
            budget.month,
            1
        )

        if budget.month == 12:
            end_date = date(
                budget.year + 1,
                1,
                1
            )
        else:
            end_date = date(
                budget.year,
                budget.month + 1,
                1
            )

        budget.spent = db.session.query(
            db.func.coalesce(
                db.func.sum(Expense.amount),
                0
            )
        ).filter(
            Expense.user_id == user_id,
            Expense.category_id == budget.category_id,
            Expense.date >= start_date,
            Expense.date < end_date
        ).scalar()

        budget.remaining = budget.amount - budget.spent

        budget.percentage = (
            budget.spent / budget.amount
        ) * 100

        budget.progress_percentage = min(budget.percentage, Decimal("100"))

    return render_template(
        "budgets/index.html",
        budgets=budget_list
    )

@budgets.route("/add", methods=["GET", "POST"])
@login_required
def add_budget():
    user_id = session["user_id"]

    categories = Category.query.filter_by(
        user_id=user_id,
        type = "expense"
    ).order_by(
        Category.name.asc()
    ).all()

    if request.method == "POST":

        category_id = request.form.get("category_id")
        amount = request.form.get("amount", "").strip()
        month = request.form.get("month", "").strip()
        year = request.form.get("year", "").strip()

        # Required fields
        if not category_id or not amount or not month or not year:
            flash("All fields are required.", "error")
            return render_template(
                "budgets/add.html",
                categories=categories
            )

        # Validate amount
        try:
            amount = Decimal(amount)
        except (InvalidOperation, TypeError):
            flash("Invalid budget amount.", "error")
            return render_template(
                "budgets/add.html",
                categories=categories
            )

        if amount <= 0:
            flash(
                "Budget amount must be greater than zero.",
                "error"
            )
            return render_template(
                "budgets/add.html",
                categories=categories
            )

        # Validate month
        try:
            month = int(month)
        except ValueError:
            flash("Invalid month.", "error")
            return render_template(
                "budgets/add.html",
                categories=categories
            )

        if month < 1 or month > 12:
            flash("Month must be between 1 and 12.", "error")
            return render_template(
                "budgets/add.html",
                categories=categories
            )

        # Validate year
        try:
            year = int(year)
        except ValueError:
            flash("Invalid year.", "error")
            return render_template(
                "budgets/add.html",
                categories=categories
            )

        if year < 2000 or year > 2100:
            flash("Invalid year.", "error")
            return render_template(
                "budgets/add.html",
                categories=categories
            )

        # Make sure the category belongs to the current user
        category = Category.query.filter_by(
            id=category_id,
            user_id=user_id,
            type = "expense"
        ).first()

        if not category:
            flash("Invalid category.", "error")
            return render_template(
                "budgets/add.html",
                categories=categories
            )

        # Prevent duplicate budgets
        existing_budget = Budget.query.filter_by(
            user_id=user_id,
            category_id=category.id,
            month=month,
            year=year
        ).first()

        if existing_budget:
            flash(
                "A budget already exists for this category and month.",
                "error"
            )
            return render_template(
                "budgets/add.html",
                categories=categories
            )

        # Create budget
        budget = Budget(
            user_id=user_id,
            category_id=category.id,
            amount=amount,
            month=month,
            year=year
        )

        db.session.add(budget)
        db.session.commit()

        flash("Budget created successfully.", "success")

        return redirect(
            url_for("budgets.list_budgets")
        )

    return render_template(
        "budgets/add.html",
        categories=categories
    )


@budgets.route(
    "/<int:budget_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_budget(budget_id):
    user_id = session["user_id"]

    # Only allow the current user to access their own budget
    budget = Budget.query.filter_by(
        id=budget_id,
        user_id=user_id
    ).first_or_404()

    categories = Category.query.filter_by(
        user_id=user_id,
        type = "expense"
    ).order_by(
        Category.name.asc()
    ).all()

    if request.method == "POST":

        category_id = request.form.get("category_id")
        amount = request.form.get("amount", "").strip()
        month = request.form.get("month", "").strip()
        year = request.form.get("year", "").strip()

        # Required fields
        if not category_id or not amount or not month or not year:
            flash("All fields are required.", "error")
            return render_template(
                "budgets/edit.html",
                budget=budget,
                categories=categories
            )

        # Validate amount using Decimal
        try:
            amount = Decimal(amount)
        except (InvalidOperation, TypeError):
            flash("Invalid budget amount.", "error")
            return render_template(
                "budgets/edit.html",
                budget=budget,
                categories=categories
            )

        if amount <= 0:
            flash(
                "Budget amount must be greater than zero.",
                "error"
            )
            return render_template(
                "budgets/edit.html",
                budget=budget,
                categories=categories
            )

        # Validate month
        try:
            month = int(month)
        except ValueError:
            flash("Invalid month.", "error")
            return render_template(
                "budgets/edit.html",
                budget=budget,
                categories=categories
            )

        if month < 1 or month > 12:
            flash("Month must be between 1 and 12.", "error")
            return render_template(
                "budgets/edit.html",
                budget=budget,
                categories=categories
            )

        # Validate year
        try:
            year = int(year)
        except ValueError:
            flash("Invalid year.", "error")
            return render_template(
                "budgets/edit.html",
                budget=budget,
                categories=categories
            )

        if year < 2000 or year > 2100:
            flash("Invalid year.", "error")
            return render_template(
                "budgets/edit.html",
                budget=budget,
                categories=categories
            )

        # Make sure category belongs to the current user
        category = Category.query.filter_by(
            id=category_id,
            user_id=user_id,
            type = "expense"
        ).first()

        if not category:
            flash("Invalid category.", "error")
            return render_template(
                "budgets/edit.html",
                budget=budget,
                categories=categories
            )

        # Prevent duplicate budgets.
        # Exclude the budget currently being edited.
        existing_budget = Budget.query.filter(
            Budget.user_id == user_id,
            Budget.category_id == category.id,
            Budget.month == month,
            Budget.year == year,
            Budget.id != budget.id
        ).first()

        if existing_budget:
            flash(
                "A budget already exists for this category and month.",
                "error"
            )
            return render_template(
                "budgets/edit.html",
                budget=budget,
                categories=categories
            )

        # Update budget
        budget.category_id = category.id
        budget.amount = amount
        budget.month = month
        budget.year = year

        db.session.commit()

        flash("Budget updated successfully.", "success")

        return redirect(
            url_for("budgets.list_budgets")
        )

    return render_template(
        "budgets/edit.html",
        budget=budget,
        categories=categories
    )


@budgets.route(
    "/<int:budget_id>/delete",
    methods=["POST"]
)
@login_required
def delete_budget(budget_id):
    user_id = session["user_id"]

    # Only allow the current user to delete their own budget
    budget = Budget.query.filter_by(
        id=budget_id,
        user_id=user_id
    ).first_or_404()

    db.session.delete(budget)
    db.session.commit()

    flash("Budget deleted successfully.", "success")

    return redirect(
        url_for("budgets.list_budgets")
    )