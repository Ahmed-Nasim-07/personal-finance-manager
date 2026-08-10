from datetime import date

from flask import Blueprint, render_template, request, redirect, url_for, session

from app.extensions import db
from app.models.expense import Expense


expenses = Blueprint(
    "expenses",
    __name__,
    url_prefix="/expenses",
)


@expenses.route("/")
def list_expenses():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    expenses_list = Expense.query.filter_by(
        user_id=session["user_id"]
    ).order_by(Expense.date.desc()).all()

    return render_template(
        "expenses/list.html",
        expenses=expenses_list,
    )


@expenses.route("/add", methods=["GET", "POST"])
def add_expense():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    if request.method == "POST":
        amount = request.form.get("amount")
        description = request.form.get("description")
        expense_date = request.form.get("date")

        if not amount or not expense_date:
            return "Amount and date are required", 400

        expense = Expense(
            user_id = session["user_id"],
            amount=amount,
            description=description,
            date=date.fromisoformat(expense_date),
        )

        db.session.add(expense)
        db.session.commit()

        return redirect(url_for("expenses.list_expenses"))

    return render_template("expenses/add.html")

@expenses.route("/<int:expense_id>/edit", methods=["GET", "POST"])
def edit_expense(expense_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    expense = Expense.query.filter_by(
        id=expense_id,
        user_id=session["user_id"]
    ).first_or_404()

    if request.method == "POST":
        expense.amount = request.form.get("amount")
        expense.description = request.form.get("description")
        expense.date = date.fromisoformat(
            request.form.get("date")
        )

        db.session.commit()

        return redirect(url_for("expenses.list_expenses"))

    return render_template(
        "expenses/edit.html",
        expense=expense
    )

@expenses.route("/<int:expense_id>/delete", methods=["POST"])
def delete_expense(expense_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    expense = Expense.query.filter_by(
        id=expense_id,
        user_id=session["user_id"]
    ).first_or_404()

    db.session.delete(expense)
    db.session.commit()

    return redirect(url_for("expenses.list_expenses"))