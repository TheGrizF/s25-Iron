import os
from flask import Flask
from flask_session import Session
from datetime import timedelta
from database import db, init_db
from backend.routes.auth_routes import auth_bp
from backend.routes.profile_routes import profile_bp
from backend.routes.daily_dish_routes import daily_dish_bp
from backend.routes.restaurant_routes import restaurant_bp
from backend.routes.dish_routes import dish_bp
from database.tasteMatching import updateAllTasteComparisons


def create_app():
    app = Flask(__name__, template_folder='../app/templates', static_folder='../app/static')

    # session configuration
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['SESSION_PERMANENT'] = True

    # initialize Flask-Session
    Session(app)

    # initialize database
    init_db(app)

    # run taste comparison updates
    with app.app_context():
        updateAllTasteComparisons()

    # register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(daily_dish_bp)
    app.register_blueprint(restaurant_bp)
    app.register_blueprint(dish_bp)

    return app