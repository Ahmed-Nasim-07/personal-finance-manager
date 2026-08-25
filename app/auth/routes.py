from flask import (Blueprint, render_template, request, redirect, url_for, session, flash)
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from app.extensions import db
from app.models.user import User


auth = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username or not email or not password:
            flash("All fields are required.", "error")
            return render_template("auth/register.html")

        existing_email = User.query.filter_by(
            email=email
        ).first()

        if existing_email:
            flash("Email already registered.", "error")
            return render_template("auth/register.html")

        existing_username = User.query.filter_by(
            username=username
        ).first()

        if existing_username:
            flash("Username already taken.", "error")
            return render_template("auth/register.html")

        password_hash = generate_password_hash(password)

        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
        )

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully. You can now log in.", "success")

        return redirect(url_for("auth.register"))

    return render_template("auth/register.html")

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("auth/login.html")

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Invalid email or password.", "error")
            return render_template("auth/login.html")

        if not check_password_hash(user.password_hash, password):
            flash("Invalid email or password.", "error")
            return render_template("auth/login.html")

        session["user_id"] = user.id

        return redirect(url_for("main.home"))

    return render_template("auth/login.html")

@auth.route("/logout")
def logout():
    session.pop("user_id", None)

    return redirect(url_for("auth.login"))

@auth.route("/whoami")
def whoami():
    user_id = session.get("user_id")

    return f"Current user ID: {user_id}"