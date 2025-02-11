from flask import Blueprint, render_template, request, redirect, url_for, flash
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

    return redirect(url_for('auth.index'))

@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email).first()

    if user:
        return redirect(url_for('daily_dish.daily_dish'))
    else:
        flash("Invalid login. Please try again.", "error")
        return redirect(url_for('auth.index'))
