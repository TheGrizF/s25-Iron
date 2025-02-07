import os

basedir = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(basedir, '../../database/tastebuddies.db')

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{database_path}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False