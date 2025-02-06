from flask import Flask, jsonify, request
import sqlite3
from app import app

print("IM IN ROUTESw")

# API route to fetch mock user data
@app.route('/api/user', methods=['GET'])
def get_user():
    user = {'username': 'Dr. SMock'}  # Mock user data
    return jsonify(user)

# API route to handle Add User form submission
@app.route('/api/addUser', methods=['POST'])
def add_user():
    # Get JSON data from the request
    data = request.get_json()
    firstName = data.get('firstName')
    lastName = data.get('lastName')
    email = data.get('email')

    # Validate data
    if not firstName or not lastName or not email:
        return jsonify({'error': 'Invalid data'}), 400

    # Connect to SQLite and insert user
    try:
        conn = sqlite3.connect('database/tastebuddies.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user (firstName, lastName, email) 
            VALUES (?, ?, ?)
        """, (firstName, lastName, email))
        conn.commit()
        conn.close()
        return jsonify({'message': 'User added successfully'}), 200
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Failed to add user'}), 500
