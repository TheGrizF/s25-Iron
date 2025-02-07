from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from .api import users
from .config import Config
from .database import db



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    db.init_app(app)
    migrate = Migrate(app, db)
    app.register_blueprint(users.bp, url_prefix='/api/users')

    return app