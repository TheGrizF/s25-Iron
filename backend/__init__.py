import os
from flask import Flask, session
from database import db
from backend.routes.auth_routes import auth_bp
from backend.routes.profile_routes import profile_bp
from backend.routes.daily_dish_routes import daily_dish_bp
from database.tasteMatching import updateAllTasteComparisons
from flask_session import Session
from datetime import timedelta

print("I AM IN BACKEND INIT.PY")

def create_app():
    app = Flask(__name__, template_folder='../app/templates', static_folder='../app/static')
    
    # session configuration
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['SESSION_PERMANENT'] = True
    
    # initialize Flask-Session
    Session(app)

    # make sure sessions are permanent by default
    @app.before_request
    def make_session_permanent():
        session.permanent = True
    
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, '../database/tastebuddies.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"

    db.init_app(app)  # initialize db within app context

    with app.app_context():
        from database.database_setup import init_db
        init_db()
        updateAllTasteComparisons()

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(daily_dish_bp)

    return app
