from flask import Blueprint, render_template, request, redirect, url_for, session
from database.models import User
from database import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
@auth_bp.route('/index')
def index():
    return render_template('index.html')

@auth_bp.route('/addUserPage')
def add_user_page():
    return render_template('addUser.html')

@auth_bp.route('/addUser', methods=['POST'])
def add_user():
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    email = request.form['email']

    new_user = User(firstName=firstName, lastName=lastName, email=email)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.index'))