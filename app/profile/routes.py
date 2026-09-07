from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from app.auth.utils import login_required
from app.extensions import db
from app.models.user import User


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