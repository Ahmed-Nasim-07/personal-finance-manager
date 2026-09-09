from datetime import date

from flask import Blueprint, render_template, session, request

from app.auth.utils import login_required
from app.extensions import db
from app.models.expense import Expense
from app.models.income import Income
from app.models.category import Category
from app.models.budget import Budget


main = Blueprint("main", __name__)


@main.route("/")
@login_required
def home():
    user_id = session["user_id"]

    today = date.today()

    current_year = today.year
    current_month = today.month

    monthly_data = []

    for offset in range(5, -1, -1):
        total_months = (
            current_year * 12
            + (current_month - 1)
            - offset
        )

        year = total_months // 12
        month = total_months % 12 + 1

        start_date = date(year, month, 1)

        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)

        monthly_income = db.session.query(
            db.func.coalesce(db.func.sum(Income.amount), 0)
        ).filter(
            Income.user_id == user_id,
            Income.date >= start_date,
            Income.date < end_date
        ).scalar()

        monthly_expenses = db.session.query(
            db.func.coalesce(db.func.sum(Expense.amount), 0)
        ).filter(
            Expense.user_id == user_id,
            Expense.date >= start_date,
            Expense.date < end_date
        ).scalar()

        monthly_data.append({
            "month": start_date.strftime("%b"),
            "income": monthly_income,
            "expenses": monthly_expenses,
        })

    category_period = request.args.get(
        "category_period",
        "6months"
    )

    allowed_periods = {"6months", "all"}

    if category_period not in allowed_periods:
        category_period = "6months"

    category_query = db.session.query(
        Category.name,
        db.func.coalesce(
            db.func.sum(Expense.amount),
            0
        )
    ).join(
        Expense,
        Expense.category_id == Category.id
    ).filter(
        Expense.user_id == user_id,
        Category.user_id == user_id,
        Category.type == "expense"
    )

    if category_period == "6months":
        total_months = (
            current_year * 12
            + (current_month - 1)
            - 5
        )

        six_months_ago_year = total_months // 12
        six_months_ago_month = total_months % 12 + 1

        six_months_ago = date(
            six_months_ago_year,
            six_months_ago_month,
            1
        )

        category_query = category_query.filter(
            Expense.date >= six_months_ago
        )

    category_data = category_query.group_by(
        Category.id,
        Category.name
    ).order_by(
        db.func.sum(Expense.amount).desc()
    ).all()

    category_data = [
        {
            "category": category_name,
            "amount": amount
        }
        for category_name, amount in category_data
    ]

    budget_data = []

    budgets = Budget.query.filter_by(
        user_id=user_id,
        year=current_year,
        month=current_month
    ).all()

    for budget in budgets:

        start_date = date(
            current_year,
            current_month,
            1
        )

        if current_month == 12:
            end_date = date(
                current_year + 1,
                1,
                1
            )
        else:
            end_date = date(
                current_year,
                current_month + 1,
                1
            )

        spent = db.session.query(
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

        budget_data.append({
            "category": budget.category.name,
            "budget": budget.amount,
            "spent": spent
        })

    total_income = Income.query.filter_by(
        user_id=user_id
    ).with_entities(
        db.func.sum(Income.amount)
    ).scalar() or 0

    total_expenses = Expense.query.filter_by(
        user_id=user_id
    ).with_entities(
        db.func.sum(Expense.amount)
    ).scalar() or 0

    balance = total_income - total_expenses

    recent_expenses = Expense.query.filter_by(
        user_id=user_id
    ).order_by(
        Expense.date.desc(),
        Expense.created_at.desc()
    ).limit(5).all()

    recent_income = Income.query.filter_by(
        user_id=user_id
    ).order_by(
        Income.date.desc(),
        Income.created_at.desc()
    ).limit(5).all()

    return render_template(
        "home.html",
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,
        recent_expenses=recent_expenses,
        recent_income=recent_income,
        monthly_data=monthly_data,
        category_data=category_data,
        category_period=category_period,
        budget_data=budget_data
    )