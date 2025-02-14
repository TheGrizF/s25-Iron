import sqlite3
import csv

def insert_test_data():
    print("inserting test data into the database.")
    
    # connect to SQLite database
    conn = sqlite3.connect('database/tastebuddies.db')
    cursor = conn.cursor()
    
    # dictionary of csv file paths
    csv_files = {
        'user': 'database/databaseTestData/users.csv',
        'taste_profile': 'database/databaseTestData/taste_profiles.csv',
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
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            headers = next(csv_reader)  # skip the header row
            
            placeholders = ', '.join(['?' for _ in headers]) # dynamic sql entries (super fancy!)
            query = f"INSERT INTO {table} ({', '.join(headers)}) VALUES ({placeholders})"
            
            for row in csv_reader:
                cursor.execute(query, row)
    
    # commit the transaction
    conn.commit()
    
    # close the connection
    conn.close()
    
    print("data successfully inserted into all tables.")

# only run if executed directly
if __name__ == "__main__":
    insert_test_data()
