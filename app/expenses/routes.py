from datetime import date
from decimal import Decimal, InvalidOperation
import csv
from io import StringIO, BytesIO
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, Response
from app.auth.utils import login_required
from app.extensions import db
from app.models.expense import Expense
from app.models.category import Category

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

expenses = Blueprint(
    "expenses",
    __name__,
    url_prefix="/expenses",
)

def build_expense_query():
    search = request.args.get("search", "").strip()
    category_id = request.args.get("category_id")
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    min_amount = request.args.get("min_amount") or None
    max_amount = request.args.get("max_amount") or None

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

    return query

@expenses.route("/")
@login_required
def list_expenses():

    search = request.args.get("search", "").strip()
    category_id = request.args.get("category_id")
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    min_amount = request.args.get("min_amount") or None
    max_amount = request.args.get("max_amount") or None

    page = request.args.get("page", 1, type=int)

    filters_applied = any([
        search,
        category_id,
        from_date,
        to_date,
        min_amount,
        max_amount
    ])

    query = build_expense_query()
    
    pagination = query.order_by(
            Expense.date.desc(),
            Expense.created_at.desc()
        ).paginate(
            page=page,
            per_page=10
        )

    categories = Category.query.filter_by(
        user_id=session["user_id"],
        type="expense"
    ).order_by(
        Category.name.asc()
    ).all()

    expenses_list = pagination.items
    total_records = pagination.total

    return render_template(
        "expenses/list.html",
        expenses=expenses_list,
        categories=categories,
        filters_applied=filters_applied,
        total_records = total_records,
        pagination = pagination
    )

@expenses.route("/export")
@login_required
def export_expenses():
    query = build_expense_query()

    expenses_list = query.order_by(
        Expense.date.desc(),
        Expense.created_at.desc()
    ).all()

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Date",
        "Category",
        "Description",
        "Amount"
    ])

    for expense in expenses_list:
        writer.writerow([
            expense.date.strftime("%Y-%m-%d"),
            expense.category.name,
            expense.description or "",
            f"{expense.amount:.2f}"
        ])

    response = Response(
        output.getvalue(),
        mimetype="text/csv"
    )

    response.headers["Content-Disposition"] = (
        "attachment; filename=expenses.csv"
    )

    return response

@expenses.route("/export/pdf")
@login_required
def export_expenses_pdf():
    query = build_expense_query()

    expenses_list = query.order_by(
        Expense.date.desc(),
        Expense.created_at.desc()
    ).all()

    total_expenses = sum(
        (expense.amount for expense in expenses_list),
        Decimal("0.00")
    )

    transaction_count = len(expenses_list)

    if transaction_count:
        average_expense = (
            total_expenses / transaction_count
        ).quantize(Decimal("0.01"))
    else:
        average_expense = Decimal("0.00")

    output = BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "Personal Finance Manager",
            styles["Title"]
        )
    )

    story.append(
        Paragraph(
            "Expense Report",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            f"Generated: {date.today().strftime('%d-%m-%Y')}",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "Summary",
            styles["Heading2"]
        )
    )

    summary_data = [
        ["Total Expenses", f"Rs. {total_expenses:.2f}"],
        ["Transactions", str(transaction_count)],
        ["Average Expense", f"Rs. {average_expense:.2f}"],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[80 * mm, 80 * mm]
    )

    summary_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
            ("PADDING", (0, 0), (-1, -1), 8),
        ])
    )

    story.append(summary_table)

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "Expense Details",
            styles["Heading2"]
        )
    )

    table_data = [
        ["Date", "Category", "Description", "Amount"]
    ]

    for expense in expenses_list:
        table_data.append([
            expense.date.strftime("%d-%m-%Y"),
            expense.category.name,
            expense.description or "",
            f"Rs. {expense.amount:.2f}",
        ])

    if not expenses_list:
        table_data.append([
            "",
            "",
            "No expenses found.",
            "",
        ])

    expense_table = Table(
        table_data,
        colWidths=[
            28 * mm,
            35 * mm,
            75 * mm,
            30 * mm,
        ],
        repeatRows=1
    )

    expense_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.darkgrey
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "FONTNAME",
                (0, 1),
                (-1, -1),
                "Helvetica"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                6
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "ALIGN",
                (-1, 1),
                (-1, -1),
                "RIGHT"
            ),
        ])
    )

    story.append(expense_table)

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            f"Total: Rs. {total_expenses:.2f}",
            styles["Heading3"]
        )
    )

    document.build(story)

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=expenses.pdf"
        }
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