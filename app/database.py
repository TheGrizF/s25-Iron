import sqlite3
import os
import csv

def init_db():
    # Create tables with the same schema as before
    conn = sqlite3.connect('database/tastebuddies.db')
    cursor = conn.cursor()
    
    cursor.executescript("""
    CREATE TABLE cuisine (
      cuisineID INTEGER PRIMARY KEY,
      cuisineName TEXT,
      preferenceLevel SMALLINT
    );

    CREATE TABLE restaurant (
      restaurantID INTEGER PRIMARY KEY,
      operatingHoursID INTEGER,
      reviewID INTEGER,
      dietaryRestrictions TEXT,
      location VARCHAR(50),
      ratingAverage SMALLINT,
      phoneNumber VARCHAR(14),
      menuID INTEGER,
      cleanAverage SMALLINT,
      busyAverage SMALLINT,
      FOREIGN KEY (menuID) REFERENCES menu(menuID),
      FOREIGN KEY (reviewID) REFERENCES review(reviewID),
      FOREIGN KEY (operatingHoursID) REFERENCES operatingHours(operatingHoursID)
    );

    -- [Rest of the existing schema...]
    """)
    
    conn.commit()
    conn.close()

def add_test_data():
    # Add test data using the same method as before
    conn = sqlite3.connect('database/tastebuddies.db')
    cursor = conn.cursor()
    
    csv_file_path = 'database/databaseTestData/MOCK_DATA.csv'
    with open(csv_file_path, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        for row in csv_reader:
            cursor.execute("""
                INSERT INTO user (firstName, lastName, email) 
                VALUES (?, ?, ?)
            """, row)
    
    conn.commit()
    conn.close()

def check_db():
    # Check database tables and contents
    conn = sqlite3.connect('database/tastebuddies.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    data = {}
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]
        
        data[table_name] = {
            'columns': columns,
            'rows': rows
        }
    
    conn.close()
    return data 