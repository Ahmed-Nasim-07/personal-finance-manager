from flask import session

from app.models.user import User


def inject_current_user():
    user = None

    user_id = session.get("user_id")

    if user_id:
        user = User.query.filter_by(id=user_id).first()

    return {
        "current_user": user
    }