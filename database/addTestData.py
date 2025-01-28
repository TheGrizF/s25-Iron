import sqlite3
import csv

# Connect to SQLite database
conn = sqlite3.connect('tastebuddies.db')
cursor = conn.cursor()

# Path to the CSV file
csv_file_path = '/home/nate/tasteBuddies/s25-Iron/database/databaseTestData/MOCK_DATA.csv'

# Open the CSV file and read data
with open(csv_file_path, 'r') as file:
    csv_reader = csv.reader(file)
    # Skip the header row
    next(csv_reader)
    
    # Insert each row into the user table
    for row in csv_reader:
        cursor.execute("""
            INSERT INTO user (firstName, lastName, email) 
            VALUES (?, ?, ?)
        """, row)

# Commit the transaction
conn.commit()

# Close the connection
conn.close()

print("Data successfully inserted into the user table.")
