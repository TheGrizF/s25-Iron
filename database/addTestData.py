import sqlite3
import csv
import json

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
        'live_update': 'database/databaseTestData/liveUpdate.csv',
        'friends': 'database/databaseTestData/friends.csv',
        'dish_taste_profile': 'database/databaseTestData/dish_taste_profile.csv',
        'taste_profile': 'database/databaseTestData/user_taste_profile.csv',
        'dish_restriction': 'database/databaseTestData/dish_restrictions.csv',
        'dish_allergen': 'database/databaseTestData/dish_allergies.csv'

    }

    json_files = {
        #'taste_profile': 'database/databaseTestData/tasteProfile.json',
        #'restaurant': 'database/databaseTestData/restaurant.json',
        #'dish_taste_profile': 'database/databaseTestData/dishTasteProfile.json'
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

        # loop through the json files and insert data
        for table, file_path in json_files.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    json_data = json.load(file)  # load json data

                    for entry in json_data:
                        if table == "taste_profile":
                            restrictions = json.dumps(entry["restrictions"])

                            cursor.execute(
                                "INSERT INTO taste_profile (taste_profile_id, user_id, restrictions, sweet, spicy, sour, bitter, umami, savory) "
                                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                (
                                    entry["taste_profile_id"],
                                    entry["user_id"],
                                    restrictions,
                                    entry["sweet"],
                                    entry["savory"],
                                    entry["sour"],
                                    entry["bitter"],
                                    entry["spicy"],
                                    entry["umami"],
                                )
                            )
                        
                        elif table == "restaurant":
                            restrictions = json.dumps(entry["restrictions"])

                            cursor.execute(
                                "INSERT INTO restaurant (restaurant_id, restaurant_name, restrictions, location, rating_average, phone_number, clean_average, busy_average) "
                                "VALUES (?, ?, ?, ?, ?, ?, ?, )",
                                (
                                    entry["restaurant_id"],
                                    entry["restaurant_name"],
                                    restrictions,
                                    entry["location"],
                                    entry["rating_average"],
                                    entry["phone_number"],
                                    entry["clean_average"],
                                    entry["busy_average"]
                                )
                            )

                        elif table == "dish_taste_profile":
                            restrictions = json.dumps(entry["restrictions"])

                            cursor.execute(
                                "INSERT INTO dish_taste_profile (dish_taste_profile_id, dish_id, cuisine, restrictions, sweet, spicy, sour, bitter, umami, savory) "
                                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                (
                                    entry["dish_taste_profile_id"],
                                    entry["dish_id"],
                                    entry["cuisine"],
                                    restrictions,
                                    entry["sweet"],
                                    entry["spicy"],
                                    entry["sour"],
                                    entry["bitter"],
                                    entry["umami"],
                                    entry["savory"]
                                )
                            )
            except FileNotFoundError:
                print(f"Warning: {file_path} not found, skipping {table}...")
            except Exception as e:
                print(f"Error inserting data into {table}: {e}")

        cursor.execute("""
            UPDATE restaurant 
            SET clean_average = (
                SELECT AVG(update_value) 
                FROM live_update 
                WHERE live_update.restaurant_id = restaurant.restaurant_id 
                AND update_type = 'cleanliness'
            )
        """)

        cursor.execute("""
            UPDATE restaurant 
            SET busy_average = (
                SELECT AVG(update_value) 
                FROM live_update 
                WHERE live_update.restaurant_id = restaurant.restaurant_id 
                AND update_type = 'busy_level'
            )
        """)

        # Commit the inserted data
        conn.commit()

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
