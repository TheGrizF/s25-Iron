from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from sqlalchemy import func
from database import db
from database.models.user import friends, user
import tastebuddies
from flask_bcrypt import Bcrypt

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth_bp.route('/')
@auth_bp.route('/index')
def index():
    return render_template('index.html')

@auth_bp.route('/addUserPage', methods=['GET'])
def add_user_page():
    return render_template('addUser.html')

@auth_bp.route('/addUser', methods=['POST'])
def add_user():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    password = request.form.get("password")

    if not first_name or not last_name or not email or not password:
        flash("Missing required fields.", "error")
        return redirect(url_for('auth.add_user_page'))

    exists = user.query.filter_by(email=email).first()
    if exists:
        flash("Email already attached to an account.", "error")
        return redirect(url_for("auth.add_user_page"))

    new_user = user(first_name=first_name, last_name=last_name, email=email)
    new_user.password = password  # Automatically hashes password

    db.session.add(new_user)
    db.session.commit()
    
    session["user_id"] = new_user.user_id  
    return redirect(url_for("profile.taste_profile"))

@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    selected_user = user.query.filter_by(email=email).first()

    if selected_user and selected_user.check_password(password):  # Verify hashed password
        session["user_id"] = selected_user.user_id
        return redirect(url_for("profile.view_profile"))
    else:
        flash("Invalid email or password. Please try again.", "error")
        return redirect(url_for("auth.index"))

@auth_bp.route("/changePassword", methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        email = request.form.get("email")
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        user_obj = user.query.filter_by(email=email).first()

        if not user_obj:
            flash("No account found with that email.", "error")
            return redirect(url_for("auth.change_password"))

        if not user_obj.check_password(old_password):
            flash("Current password is incorrect.", "error")
            return redirect(url_for("auth.change_password"))

        if new_password != confirm_password:
            flash("New passwords do not match.", "error")
            return redirect(url_for("auth.change_password"))

        # Hash the new password before saving
        user_obj.password = new_password  # This automatically hashes the password
        db.session.commit()

        flash("Password updated successfully!", "success")
        return redirect(url_for("auth.index"))

    return render_template("change_password.html")

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('auth.index'))

@auth_bp.route('/TasteBuds', methods=['GET', 'POST'])
def searchUser():
    userName = request.form.get('userName', "").strip()
    current_user_id = session.get('user_id')  # Renamed to avoid conflict with model

    if not userName:
        flash("Enter a name or email to find your buddy")
        return redirect(url_for('daily_dish.TasteBuds'))

    search = userName.split()

    # Default values
    first_name, last_name = None, None
    if len(search) == 1:
        first_name = search[0]
    elif len(search) > 1:
        first_name = search[0]
        last_name = search[1]

    # Check for email - Case insensitive
    if "@" in userName:
        found_user = user.query.filter(func.lower(user.email) == userName.lower()).first()
    else:
        # Case insensitive search by first and last name
        matches = user.query.filter(func.lower(user.first_name) == first_name.lower())
        if last_name:
            matches = matches.filter(func.lower(user.last_name) == last_name.lower())
        found_user = matches.first()

    if found_user:
        if found_user.user_id == current_user_id:
            return redirect(url_for('profile.view_profile'))
        else:
            return redirect(url_for('profile.viewUserProfile', user_id=found_user.user_id))

    flash("No user found")
    return redirect(url_for('daily_dish.TasteBuds'))


@auth_bp.route('/addFriend/<user_id>', methods=['POST', 'GET'])
def addFriend(user_id):
    current_user_id = session.get('user_id')  # Renamed to avoid conflict

    if not current_user_id:
        flash("You must be logged in to add a friend.", "error")
        return redirect(url_for('auth.index'))

    # Check if already Friends
    exists = friends.query.filter_by(user_id=current_user_id, buddy_id=user_id).first()
    
    if exists:
        flash("Buddy already added", "info")
    else:
        new_friend = friends(user_id=current_user_id, buddy_id=user_id, status="accepted")
        db.session.add(new_friend)
        db.session.commit()
        flash("Buddy added", "success")

    return redirect(url_for('profile.viewUserProfile', user_id=user_id))

@auth_bp.route('/database')
def database():
    return render_template('database.html')

@auth_bp.route('/test_database')
def test_database():
    from database import db
    from sqlalchemy.inspection import inspect

    data = {}

    # Get all table names dynamically
    models = db.Model.registry._class_registry.values()

    for model in models:
        if hasattr(model, '__tablename__'):  # Ensure it's a valid model
            table_name = model.__tablename__
            records = model.query.all()

            # Use SQLAlchemy's inspect() to get column names dynamically
            columns = [column.name for column in inspect(model).c]

            # Convert data to a dictionary format
            data[table_name] = [
                {column: getattr(record, column) for column in columns}
                for record in records
            ]

    return render_template('test_database.html', tables_data=data)