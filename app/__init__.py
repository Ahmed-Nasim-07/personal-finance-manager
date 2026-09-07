from flask import Flask
from config import Config
from app.extensions import db, migrate
from app.context_processors import inject_current_user

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.context_processor(inject_current_user)
    
    from app import models
    from app.routes import main
    app.register_blueprint(main)
    from app.expenses.routes import expenses
    app.register_blueprint(expenses)
    from app.income.routes import income_bp
    app.register_blueprint(income_bp)
    from app.auth.routes import auth
    app.register_blueprint(auth)
    from app.categories.routes import categories
    app.register_blueprint(categories)
    from app.profile.routes import profile
    app.register_blueprint(profile)

    return app