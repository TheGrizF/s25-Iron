import os
from flask import Flask
from flask_session import Session
from datetime import timedelta
from database import db, init_db
from backend.routes.auth_routes import auth_bp
from backend.routes.profile_routes import profile_bp
from backend.routes.daily_dish_routes import daily_dish_bp
from database.tasteMatching import updateAllTasteComparisons
from backend.utils import get_dish_recommendations

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
        recs = get_dish_recommendations(user_id=12)
        print('dishes:', recs)

    # register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(daily_dish_bp)

    return app