import os
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask import Flask
from database.addTestData import insert_test_data

print("I AM IN DATABASE INIT")

# Initialize SQLAlchemy and Bcrypt
db = SQLAlchemy()
bcrypt = Bcrypt()

def init_db(app):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, 'tastebuddies.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    bcrypt.init_app(app)

    with app.app_context():
        # Import models inside app context to avoid circular imports
        from database.models.dish import dish, menu, menuDishJunction
        from database.models.restaurant import restaurant, operatingHours, liveUpdate
        from database.models.review import review
        from database.models.taste_profiles import tasteProfile, dishTasteProfile
        from database.models.user import user, tasteComparisons, cuisine, cuisineUserJunction, friends, savedDishes, savedRestaurants

        # Create tables if the database does not exist
        if not os.path.exists(db_path):
            print("Database not found. Creating it!")
            db.create_all()
            print("Database tables created successfully.")

        # Check if the database has data, if not, populate it
        if not user.query.first():
            print("Database is empty. Populating with test data!")
            insert_test_data()
        else:
            print("Database already populated.")
