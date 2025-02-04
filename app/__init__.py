from flask import Flask
import os
import subprocess
import sqlite3
print("IM IN INIT")

# path to the database file
db_path = os.path.join("database", "tastebuddies.db")

# check if the database file exists
if not os.path.exists(db_path):
    print("Database not found. Running database.py to create it...")
    subprocess.run(["python3", "database/database.py"])
else:
    print("Database already exists.")

# connect to the database
conn = sqlite3.connect("database/tastebuddies.db")
cursor = conn.cursor()

# check if "Tyson" exists in the user table
cursor.execute("SELECT COUNT(*) FROM user WHERE firstName = ?", ("Tyson",))
result = cursor.fetchone()[0]

conn.close()

# if "Tyson" is not found, run addTestData.py
if result == 0:
    print("Tyson not found in database. Running addTestData.py to insert data...")
    subprocess.run(["python3", "database/addTestData.py"])
else:
    print("addTestData.py has already been ran.")


app = Flask(__name__)

from app import routes