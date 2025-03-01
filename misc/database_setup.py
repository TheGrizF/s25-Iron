import os
from database import db
from flask import Flask
from database.addTestData import insert_test_data

print("I AM IN DATABASE_SETUP.PY")

def init_db():
    app = Flask(__name__)

    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, 'tastebuddies.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    if not os.path.exists(db_path):
        print("Database not found. Creating and populating it!")
        with app.app_context():
            from database.models import User, TasteProfile, Cuisine, Dish, Restaurant, Review, SavedDishes, SavedRestaurants, TasteBuddies, OperatingHours, Menu
            db.create_all()
            print("Database tables created successfully.")
    else:
        print("Database exists. Population check!")
        
    with app.app_context():
        from database.models import User
        if not User.query.first():
            print("Database is empty. Populating with test data!")
            insert_test_data()
        else:
            print("Database already populated.")

if __name__ == "__main__":
    init_db()
