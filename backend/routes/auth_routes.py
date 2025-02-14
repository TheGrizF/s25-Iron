from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.models import User
from database import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
@auth_bp.route('/index')
def index():
    return render_template('index.html')

@auth_bp.route('/addUserPage', methods=['GET'])
def add_user_page():
    return render_template('addUser.html')

@auth_bp.route('/addUser', methods=['POST'])
def add_user():
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    email = request.form['email']

    # Check for already in database
    exists = User.query.filter_by(email=email).first()
    if exists:
        flash('Email already attached to an account.', 'error')
        return redirect(url_for('auth.add_user_page'))

    new_user = User(firstName=firstName, lastName=lastName, email=email)
    
    db.session.add(new_user)
    db.session.commit()
    session['user_id'] = new_user.userID
    return redirect(url_for('profile.taste_profile'))

@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email).first()

    if user:
        session['user_id'] = user.userID
        return redirect(url_for('profile.view_profile'))
    else:
        flash("Invalid login. Please try again.", "error")
        return redirect(url_for('auth.index'))
    
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('auth.index'))

@auth_bp.route('/database')
def database():
    return render_template('database.html')

@auth_bp.route('/test_database')
def test_database():
    from database import db
    from database.models import User

    data = {}
    users = User.query.all()

    for u in users:
        print(f"User: {u.firstName} {u.lastName}")
    if u.taste_profile:
        print(f"  Dietary Restrictions: {u.taste_profile.dietaryRestrictions}")
    else:
        print("  No taste profile found")


    data['users'] = [{
        'firstName': u.firstName, 
        'lastName': u.lastName, 
        'email': u.email,
        'tasteProfile': {
            'sweet': u.taste_profile.sweet if u.taste_profile else None,
            'spicy': u.taste_profile.spicy if u.taste_profile else None,
            'sour': u.taste_profile.sour if u.taste_profile else None,
            'bitter': u.taste_profile.bitter if u.taste_profile else None,
            'umami': u.taste_profile.umami if u.taste_profile else None,
            'savory': u.taste_profile.savory if u.taste_profile else None,
            'dietaryRestrictions': u.taste_profile.dietaryRestrictions if u.taste_profile else None
        }    
    } for u in users]

    return render_template('test_database.html', tables_data=data)