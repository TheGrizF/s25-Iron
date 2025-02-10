import os
import subprocess
from database import db
from flask import Flask


def init_db():
  app = Flask(__name__)

  base_dir = os.path.abspath(os.path.dirname(__file__))
  db_path = os.path.join(base_dir, 'tastebuddies.db')
  app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

  db.init_app(app)

  if not os.path.exists(db_path):
    print("Database not found. Running database.py to create it...")
    subprocess.run(["python", "database/database.py"])
  else:
    print("Database exists. Population check...")

  with app.app_context():
    from database.models import User, TasteProfile, Cuisine, Dish, Restaurant, Review, SavedDishes, SavedRestaurants, TasteBuddies, OperatingHours, Menu
  
    db.create_all()
    print("Database tables created successfully.")

    if not User.query.filter_by(firstName="Tyson").first():
      print("Tyson not found in database. Running addTestData.py to insert data...")
      subprocess.run(["python", "database/addTestData.py"])
    else:
      print("Database previously populated.")

if __name__ == "__main__":
    init_db()
