import sys
import os

# Add the path to the parent directory so Python can find 'backend'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.app.database import db
from backend.app.models import User, Restaurant, Dish

app = create_app()

with app.app_context():
    tyson_exists = User.query.filter_by(firstName="Tyson").first()

    if not tyson_exists:
        print("Seeding database with test data...")

        # Add a test user
        user1 = User(firstName="Tyson", lastName="Bonnessen", email="tbonnessen0@bloglovin.com")
        user2 = User(firstName="Charla", lastName="Frichley", email="cfrichley2@blogs.com")

        # Add a test restaurant
        restaurant1 = Restaurant(
            restaurantName="High Side",
            dietaryRestrictions="Vegetarian",
            location="4009 Chain Bridge Rd",
            ratingAverage=4,
            phoneNumber="861-555-4009"
        )

        # Add a test dish
        dish1 = Dish(
            dishName="Spicy Dan-Dan Noodles",
            featured=True,
            available=True
        )

        # Commit all test data to the database
        db.session.add_all([user1, user2, restaurant1, dish1])
        db.session.commit()

        print("Test data added successfully!")
    else:
        print("Test data already exists. No changes made.")