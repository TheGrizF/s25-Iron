import os
from flask import Flask, session
from database import db
from backend.routes.auth_routes import auth_bp
from backend.routes.profile_routes import profile_bp
from backend.routes.daily_dish_routes import daily_dish_bp
from flask_session import Session
from datetime import timedelta

def create_app():
    app = Flask(__name__, template_folder='../app/templates', static_folder='../app/static')
    
    # Session configuration
    app.config['SECRET_KEY'] = 'your-secret-key'  # Make sure this is set
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['SESSION_PERMANENT'] = True
    
    # Initialize Flask-Session
    Session(app)
    
    # Make sure sessions are permanent by default
    @app.before_request
    def make_session_permanent():
        session.permanent = True
    
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, '../database/tastebuddies.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"

    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(daily_dish_bp)

    return app