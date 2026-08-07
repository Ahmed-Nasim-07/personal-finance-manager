
class Config:
    """Base configuration for the application."""

    SECRET_KEY = "change-me"
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///finance.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False