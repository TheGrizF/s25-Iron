from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from app import app

print("IM IN ROUTES")

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Dr. SMock'} #mock user
    return render_template('index.html', title='Home', user=user)

# Route to display the Add User form
@app.route('/addUserPage')
def addUserPage():
    return render_template('addUser.html')

# Route to handle Add User form submission
@app.route('/addUser', methods=['POST'])
def addUser():
    # Get form data
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    email = request.form['email']
    
    # Connect to SQLite and insert user
    conn = sqlite3.connect('database/tastebuddies.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user (firstName, lastName, email) 
        VALUES (?, ?, ?)
    """, (firstName, lastName, email))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route('/test_database')
def test_database():
    # Connect to SQLite and get data
    conn = sqlite3.connect('database/tastebuddies.db')
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    # Get data from each table
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
    return render_template('test_database.html', tables_data=data)

@app.route('/database')
def database():
    return render_template('database.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/restaurants')
def restaurants():
    return render_template('restaurants.html')

@app.route('/restaurant/<id>')
def restaurant_detail(id):
    return render_template('restaurant_detail.html')

@app.route('/api/taste-profile', methods=['POST'])
def save_taste_profile():
    try:
        data = request.get_json()
        
        conn = sqlite3.connect('database/tastebuddies.db')
        cursor = conn.cursor()
        
        # Insert into tasteProfile table
        cursor.execute("""
            INSERT INTO tasteProfile (
                dietaryRestrictions,
                sweet,
                salty,
                sour,
                bitter,
                umami
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data['dietaryRestrictions'],
            data['tasteScores']['sweet'],
            data['tasteScores']['salty'],
            data['tasteScores']['sour'],
            data['tasteScores']['bitter'],
            data['tasteScores']['umami']
        ))
        
        profile_id = cursor.lastrowid
        
        # Update user table with the new taste profile ID
        cursor.execute("""
            UPDATE user 
            SET tasteProfileID = ? 
            WHERE userID = ?
        """, (profile_id, data['userId']))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        print(f"Error saving taste profile: {str(e)}")
        return jsonify({'error': 'Failed to save taste profile'}), 500

@app.route('/taste-profile')
def taste_profile():
    return render_template('tasteProfile.html')
