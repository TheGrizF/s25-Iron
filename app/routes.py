from flask import Flask, render_template, request, redirect, url_for
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
