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
        'user': 'database/databaseTestData/users.csv',
        'cuisine': 'database/databaseTestData/cuisines.csv',
        'dish': 'database/databaseTestData/dishes.csv',
        'restaurant': 'database/databaseTestData/restaurants.csv',
        'review': 'database/databaseTestData/reviews.csv',
        'saved_dishes': 'database/databaseTestData/saved_dishes.csv',
        'saved_restaurants': 'database/databaseTestData/saved_restaurants.csv',
        'taste_buddies': 'database/databaseTestData/taste_buddies.csv',
        'operating_hours': 'database/databaseTestData/operating_hours.csv',
        'menu': 'database/databaseTestData/menus.csv'
    }
    
    # loop through the csv files and insert data
    for table, file_path in csv_files.items():
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            headers = next(csv_reader)  # skip the header row
            
            placeholders = ', '.join(['?' for _ in headers])  # dynamic sql entries
            query = f"INSERT INTO {table} ({', '.join(headers)}) VALUES ({placeholders})"
            
            for row in csv_reader:
                cursor.execute(query, row)

    # handle taste_profiles.json separately
    json_file = 'database/databaseTestData/taste_profiles.json'
    
    with open(json_file, 'r', encoding='utf-8') as file:
        taste_profiles = json.load(file)  # load json data

        for entry in taste_profiles:
            # convert dietaryRestrictions json object to a string before inserting
            dietary_restrictions = json.dumps(entry["dietaryRestrictions"])

            cursor.execute("""
                INSERT INTO taste_profile (tasteProfileID, userID, dietaryRestrictions, sweet, spicy, sour, bitter, umami, savory, cuisineID)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry["tasteProfileID"],
                entry["userID"],
                dietary_restrictions,
                entry["sweet"],
                entry["spicy"],
                entry["sour"],
                entry["bitter"],
                entry["umami"],
                entry["savory"],
                entry["cuisineID"]
            ))

    # commit the transaction
    conn.commit()
    
    # close the connection
    conn.close()
    
    print("data successfully inserted into all tables.")

# only run if executed directly
if __name__ == "__main__":
    insert_test_data()
