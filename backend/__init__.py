import os
from flask import Flask
from database import db
from backend.routes.auth_routes import auth_bp
from backend.routes.profile_routes import profile_bp
from backend.routes.daily_dish_routes import daily_dish_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 't4st3budd13s_s3cr3t_k3y'

    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, '../database/tastebuddies.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"

    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(daily_dish_bp)

    return app