from flask import Blueprint, render_template, session

from app.auth.utils import login_required
from app.extensions import db
from app.models.expense import Expense
from app.models.income import Income


main = Blueprint("main", __name__)


@main.route("/")
@login_required
def home():
    user_id = session["user_id"]

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
        Expense.date.desc()
    ).limit(5).all()

    recent_income = Income.query.filter_by(
        user_id=user_id
    ).order_by(
        Income.date.desc()
    ).limit(5).all()

    return render_template(
        "home.html",
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,
        recent_expenses=recent_expenses,
        recent_income=recent_income,
    )