from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from sqlalchemy import func, or_
from backend.utils import normalize_email
from database import db, bcrypt
from database.models.taste_profiles import tasteProfile
from database.models.user import friends, user
import tastebuddies
from flask_bcrypt import Bcrypt
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
@auth_bp.route('/index')
def index():
    return render_template('index.html')

@auth_bp.route('/addUserPage', methods=['GET'])
def add_user_page():
    return render_template('addUser.html')

"""
    Displays the form for adding a new user account.
    This form allows users to input their first name, last name, email, and select a profile icon.
    It returns the 'addUser.html' template to collect this information.
"""

@auth_bp.route('/addUser', methods=['POST'])
def add_user():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = normalize_email(request.form.get("email"))
    password = request.form.get("password")
    icon_path = request.form.get("icon_path") or "images/profile_icons/default1.png"
    print(icon_path)

    """
     Processes the submitted user registration and creates a new user and taste profile in the database.
     It performs validation, checks for duplicate email addresses, and saves user data if valid.
     After registration, it redirects the user to the taste profile page and stores the user ID in the session.
 
     """

    if not first_name or not last_name or not email or not password:
        flash("Missing required fields.", "error")
        return redirect(url_for('auth.add_user_page'))

    if not is_valid_email(email):
        flash("Invalid email format.", "error")
        return redirect(url_for("auth.add_user_page"))

    exists = user.query.filter_by(email=email).first()
    if exists:
        flash("Email already attached to an account.", "error")
        return redirect(url_for("auth.add_user_page"))
    
    new_user = user(
        first_name=first_name, 
        last_name=last_name, 
        email=email,
        password=password,
        icon_path=icon_path)

    db.session.add(new_user)
    db.session.commit()

    taste_profile = tasteProfile(user_id=new_user.user_id, current_step=1)
    db.session.add(taste_profile)
    db.session.commit()
    
    session["user_id"] = new_user.user_id  
    return redirect(url_for("profile.taste_profile"))

def is_valid_email(email):
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(email_regex, email) is not None


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    """
    This function Handles the user login with a form on the login page.
    If the method is POST, it verifies the email and logs in the user if a match is found in the database.
    If the login is successful, it redirects to the user's taste  profile page; otherwise, it shows an error and returns to the index.

    """
    if request.method == 'POST':
        email = normalize_email(request.form.get("email"))
        password = request.form.get("password")

        selected_user = user.query.filter(func.lower(user.email) == email.lower()).first()

        if selected_user  and selected_user.check_password(password):
            session["user_id"] = selected_user.user_id
            return redirect(url_for("profile.view_profile"))
        else:
            flash("Invalid email or password. Please try again.", "error")
            return redirect(url_for("auth.index"))
    else:
        return render_template("index.html")
    
@auth_bp.route("/changePassword", methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        email = normalize_email(request.form.get("email"))
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

        user_obj.password = new_password

        db.session.commit()
        flash("Password updated successfully!", "success")
        return redirect(url_for("auth.index"))

    return render_template("change_password.html")

@auth_bp.route('/logout')
def logout():

    """
    This function logs out the current user out of the application by clearing the session and redirecting them to the index page, which is the login page.
    This ensures any authenticated user is removed from the session an ends the session securely.
    A message is displayed to inform the user that they have logged out.

    """
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('auth.index'))


@auth_bp.route('/TasteBuds', methods=['GET', 'POST'])
def searchUser():

    """
    This function allows users to search for other users by username or email in order to view their profile.
    If the input includes an email, it performs a direct match; otherwise, it searches by first and/or last name.
    Results can redirect to a user profile, a list of matches, or show an error if no match is found.

    """
    userName = request.form.get('userName', "").strip()
    current_user_id = session.get('user_id')  # Renamed to avoid conflict with model

    if not userName:
        flash("Enter a name or email to find your buddy")
        return redirect(url_for('daily_dish.TasteBuds'))

    search = userName.lower().split()

    # Default values
    first_name, last_name = None, None
    if len(search) == 1:
        first_name = search[0]
    elif len(search) > 1:
        first_name = search[0]
        last_name = search[1]

    # Check for email - Case insensitive
    if "@" in userName:        
        normalized_email = normalize_email(userName)
        found_user = user.query.filter(func.lower(user.email) == normalized_email).first()
        if found_user:
            if found_user.user_id == current_user_id:
                return redirect(url_for('profile.view_profile'))
            return redirect(url_for('profile.viewUserSearchResults', user_id=found_user.user_id))
    else:
        # Case insensitive search by first and last name
        matches = user.query.filter(
            or_(
                func.lower(user.first_name) == first_name,
                func.lower(user.last_name) == first_name
            ),
            user.user_id != current_user_id
        )
        
        if last_name:
            matches = matches.filter(func.lower(user.last_name) == last_name.lower())
        
        all_matches = matches.all()
        
        if len(all_matches) == 1:
            found_user = all_matches[0]
            if found_user.user_id == current_user_id:
                return redirect(url_for('profile.view_profile'))
            return redirect(url_for('profile.viewUserSearchResults', user_id=found_user.user_id))
        
        elif len(all_matches) > 1:
            return render_template('userSearchResult.html', matches=all_matches, search_term=userName)
        
    flash("No user found", "error")
    return redirect(url_for('daily_dish.TasteBuds'))
 
@auth_bp.route('/addFriend/<user_id>', methods=['POST', 'GET'])
def addFriend(user_id):

    """
    The addFriend function adds a user as a follower of the currently logged-in user.
    It prevents duplicate entries by checking if the following already exists before adding it.
    After processing, it redirects the user back to the current page and displays a message.

    """
    current_user_id = session.get('user_id')

    if not current_user_id:
        flash("You must be logged in to follow someone.", "error")
        return redirect(url_for('auth.index'))

    exists = friends.query.filter_by(user_id=current_user_id, buddy_id=user_id).first()
    
    if exists:
        flash("You are already following this user", "info")
    else:
        new_friend = friends(user_id=current_user_id, buddy_id=user_id)
        db.session.add(new_friend)
        db.session.commit()
        flash("You are now following this user", "success")

    return redirect(request.referrer)

@auth_bp.route('/removeFriend/<user_id>', methods=['POST', 'GET'])
def removeFriend(user_id):

    """
    Removes the specified user from the current user's list of users they follow.
    This function ensures the user is logged in and that the following of the specififed user exists before deleting it from the database.
    Once removed, a confirmation message is shown that the current user does not follow the other user anymore.

    """
    current_user_id = session.get('user_id')

    if not current_user_id:
        flash("You must be logged in to unfollow someone.", "error")
        return redirect(url_for('auth.index'))

    friendship = friends.query.filter_by(user_id=current_user_id, buddy_id=user_id).first()

    if friendship:
        db.session.delete(friendship)
        db.session.commit()
        flash("You have unfollowed this user.", "success")
    else:
        flash("You are not following this user.", "error")

    return redirect(request.referrer)

@auth_bp.route('/database')
def database():

    
    """
    The databse function Renders a HTML page used to interact with the content of the database.
    This function serves as a front end for developers or administrators to view the backend data structures.
    It returns the 'database.html' template.

    """
    return render_template('database.html')

@auth_bp.route('/test_database')
def test_database():

    """
    The function inspects all SQLAlchemy models and retrieves their data for debugging.
    It collects table names, column names, and data records, and renders them in a readable format on a webpage.

    """

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