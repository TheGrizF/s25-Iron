import sqlite3
import csv

# connect to SQLite database
conn = sqlite3.connect('database/tastebuddies.db')
cursor = conn.cursor()

# path to the CSV file
csv_file_path = 'database/databaseTestData/MOCK_DATA.csv'

# open the CSV file and read data
with open(csv_file_path, 'r') as file:
    csv_reader = csv.reader(file)
    # Skip the header row
    next(csv_reader)
    
    # insert each row into the user table
    for row in csv_reader:
        cursor.execute("""
            INSERT INTO user (firstName, lastName, email) 
            VALUES (?, ?, ?)
        """, row)

# commit the transaction
conn.commit()

# close the connection
conn.close()

print("Data successfully inserted into the user table.")
