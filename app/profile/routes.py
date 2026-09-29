from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from app.auth.utils import login_required
from app.extensions import db
from app.models.user import User
from app.models.expense import Expense
from app.models.income import Income
from app.models.category import Category
from app.models.budget import Budget


profile = Blueprint("profile", __name__, url_prefix="/profile")


@profile.route("/")
@login_required
def profile_page():
    user = User.query.filter_by(
        id=session["user_id"]
    ).first_or_404()

    return render_template(
        "profile/index.html",
        user=user
    )


@profile.route("/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    user = User.query.filter_by(
        id=session["user_id"]
    ).first_or_404()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()

        if not username or not email:
            flash("Username and email are required.", "error")
            return render_template(
                "profile/edit.html",
                user=user
            )

        existing_username = User.query.filter(
            User.username == username,
            User.id != user.id
        ).first()

        if existing_username:
            flash("Username already taken.", "error")
            return render_template(
                "profile/edit.html",
                user=user
            )

        existing_email = User.query.filter(
            User.email == email,
            User.id != user.id
        ).first()

        if existing_email:
            flash("Email already registered.", "error")
            return render_template(
                "profile/edit.html",
                user=user
            )

        user.username = username
        user.email = email

        db.session.commit()

        flash("Profile updated successfully.", "success")

        return redirect(url_for("profile.profile_page"))

    return render_template(
        "profile/edit.html",
        user=user
    )

@profile.route("/delete", methods=["GET", "POST"])
@login_required
def delete_account():

    user = User.query.filter_by(
        id=session["user_id"]
    ).first_or_404()

    if request.method == "POST":

        password = request.form.get("password", "")

        if not password:
            flash("Password is required.", "error")
            return render_template(
                "profile/delete.html"
            )

        if not check_password_hash(
            user.password_hash,
            password
        ):
            flash("Incorrect password.", "error")
            return render_template(
                "profile/delete.html"
            )

        try:
            db.session.query(Expense).filter_by(
                user_id=user.id
            ).delete()

            db.session.query(Income).filter_by(
                user_id=user.id
            ).delete()

            db.session.query(Budget).filter_by(
                user_id=user.id
            ).delete()

            db.session.query(Category).filter_by(
                user_id=user.id
            ).delete()

            db.session.delete(user)

            db.session.commit()

        except Exception:
            db.session.rollback()

            flash(
                "Unable to delete your account. Please try again.",
                "error"
            )

            return render_template(
                "profile/delete.html"
            )

        session.clear()

        flash(
            "Your account has been permanently deleted.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "profile/delete.html"
    )