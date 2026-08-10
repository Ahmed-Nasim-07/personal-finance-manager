from flask import Flask
from config import Config
from app.extensions import db, migrate

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    from app import models
    from app.routes import main
    app.register_blueprint(main)
    from app.expenses.routes import expenses
    app.register_blueprint(expenses)
    from app.auth.routes import auth
    app.register_blueprint(auth)

    return app