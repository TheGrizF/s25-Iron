import sqlite3
import csv
import json
from flask_bcrypt import Bcrypt
from flask import Flask

app = Flask(__name__)
bcrypt = Bcrypt(app)

def insert_test_data():
    print("inserting test data into the database.")

    # connect to SQLite database
    conn = sqlite3.connect('database/tastebuddies.db')
    cursor = conn.cursor()

    # dictionary of csv file paths
    csv_files = {
        'user': 'database/databaseTestData/user.csv',
        'cuisine': 'database/databaseTestData/cuisine.csv',
        'dish': 'database/databaseTestData/dish.csv',
        'review': 'database/databaseTestData/review.csv',
        'saved_dishes': 'database/databaseTestData/savedDishes.csv',
        'saved_restaurants': 'database/databaseTestData/savedRestaurants.csv',
        'operating_hours': 'database/databaseTestData/operatingHours.csv',
        'menu': 'database/databaseTestData/menu.csv',
        'menu_dish_junction': 'database/databaseTestData/menuDishJunction.csv',
        'cuisine_user_junction': 'database/databaseTestData/cuisineUserJunction.csv',
        'restaurant': 'database/databaseTestData/restaurant.csv',
        #'live_update': 'database/databaseTestData/liveUpdate.csv',
        'friends': 'database/databaseTestData/friends.csv',
        'dish_taste_profile': 'database/databaseTestData/dish_taste_profile.csv',
        'taste_profile': 'database/databaseTestData/user_taste_profile.csv',
        'dish_restriction': 'database/databaseTestData/dish_restrictions.csv',
        'dish_allergen': 'database/databaseTestData/dish_allergies.csv'

    }

    try:
        # loop through the csv files and insert data
        for table, file_path in csv_files.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    csv_reader = csv.reader(file)
                    headers = next(csv_reader)  # skip the header row
                    
                    placeholders = ', '.join(['?' for _ in headers])  # dynamic sql entries
                    query = f"INSERT INTO {table} ({', '.join(headers)}) VALUES ({placeholders})"

                    cursor.executemany(query, csv_reader)  # batch insert
            except FileNotFoundError:
                print(f"Warning: {file_path} not found, skipping...")
            except Exception as e:
                print(f"Error inserting data into {table}: {e}")

        # Commit the inserted data
        conn.commit()

        # Retrieve all plaintext passwords
        cursor.execute("SELECT user_id, password_hash FROM user")
        users = cursor.fetchall()

        for user_id, password in users:
            # Check if the password is already hashed
            if not password.startswith("$2b$"):  # Bcrypt hashes start with $2b$
                print(f"Hashing password for user_id {user_id}")

                # Hash plaintext password
                hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

                # Update the password in the database
                cursor.execute("UPDATE user SET password_hash = ? WHERE user_id = ?", (hashed_password, user_id))

        conn.commit()
        print("All plaintext passwords have been hashed.")
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # close the connection
        conn.close()
        print("data successfully inserted into all tables.")

# only run if executed directly
if __name__ == "__main__":
    insert_test_data()
