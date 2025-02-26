from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from sqlalchemy import func
from database.models import User,TasteBuddies
from database import db
from datetime import datetime

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

@auth_bp.route('/TasteBuds', methods=['GET','POST'])
def searchUser():
    userName = request.form.get('userName', "").strip()
    current_user = session.get('user_id')
    
    if not userName:
        flash("Enter a name or email to find your buddy")
        return redirect(url_for('daily_dish.TasteBuds'))

    search = userName.split()

    #default values
    first_Name, last_Name = None, None
    if len(search) == 1:
        first_Name = search[0]
    if len(search) > 1:
       first_Name = search[0]  
       last_Name  = search[1] 
    

    if "@" in userName:     #check for email - Case insensitive
        user = User.query.filter(func.lower(User.email) == userName.lower()).first()
    else:
        #case insensitive by first and last (if given)
        matches = User.query.filter(func.lower(User.firstName) == first_Name.lower())
        if last_Name:
            matches = matches.filter(func.lower(User.lastName) == last_Name.lower())
        user = matches.first()

    if user:
        if user.userID == current_user:
            return redirect(url_for('profile.view_profile'))
        else:
            return redirect(url_for('profile.viewUserProfile',user_id=user.userID))
    else:
       flash("No user found")
    return redirect(url_for('daily_dish.TasteBuds'))
    
       
@auth_bp.route('/addFriend/<user_id>', methods=['POST','GET'])
def addFriend(user_id):
    user = session.get('user_id')

    #Check if already Friends
    exists = TasteBuddies.query.filter_by(userID=user,buddyID=user_id).first()
    
    if exists:
        flash("Buddy already added")
    else:
        new_friend = TasteBuddies(userID=user, buddyID=user_id, dateAdded=datetime.now())
        db.session.add(new_friend)
        db.session.commit()
        flash("Buddy Added")
    return redirect(url_for('profile.viewUserProfile',user_id=user_id))


@auth_bp.route('/database')
def database():
    return render_template('database.html')

@auth_bp.route('/test_database')
def test_database():
    from database import db
    from database.models import User, TasteProfile, Cuisine, Review, SavedDishes, SavedRestaurants, TasteBuddies, Restaurant, Menu, Dish, OperatingHours

    data = {}

    # fetch users
    users = User.query.all()
    data['users'] = [{
        'userID': u.userID,  # primary key
        'firstName': u.firstName,
        'lastName': u.lastName,
        'email': u.email,
        'userRole': u.userRole,
        'tasteBuddiesID': u.tasteBuddiesID,  # foreign key
        'savedRestaurantsID': u.savedRestaurantsID,  # foreign key
        'tasteProfileID': u.tasteProfileID,  # foreign key
        'reviewID': u.reviewID,  # foreign key
        'savedDishesID': u.savedDishesID  # foreign key
    } for u in users]

    # fetch taste profiles
    taste_profiles = TasteProfile.query.all()
    data['taste_profiles'] = [{
        'tasteProfileID': tp.tasteProfileID,  # primary key
        'userID' : tp.userID,
        'dietaryRestrictions': tp.dietaryRestrictions,
        'sweet': tp.sweet,
        'sour': tp.sour,
        'bitter': tp.bitter,
        'umami': tp.umami,
        'savory': tp.savory,
        'cuisineID': tp.cuisineID  # foreign key
    } for tp in taste_profiles]

    # fetch cuisines
    cuisines = Cuisine.query.all()
    data['cuisines'] = [{
        'cuisineID': c.cuisineID,  # primary key
        'cuisineName': c.cuisineName,
        'preferenceLevel': c.preferenceLevel
    } for c in cuisines]

    # fetch restaurants
    restaurants = Restaurant.query.all()
    data['restaurants'] = [{
        'restaurantID': r.restaurantID,  # primary key
        'restaurantName': r.restaurantName,
        'location': r.location,
        'phoneNumber': r.phoneNumber,
        'operatingHoursID': r.operatingHoursID,  # foreign key
        'reviewID': r.reviewID,  # foreign key
        'menuID': r.menuID,  # foreign key
        'dietaryRestrictions': r.dietaryRestrictions
    } for r in restaurants]

    # fetch dishes
    dishes = Dish.query.all()
    data['dishes'] = [{
        'dishID': d.dishID,  # primary key
        'dishName': d.dishName,
        'featured': d.featured,
        'available': d.available,
        'dishTasteProfileID': d.dishTasteProfileID  # foreign key
    } for d in dishes]

    # fetch reviews
    reviews = Review.query.all()
    data['reviews'] = [{
        'reviewID': r.reviewID,  # primary key
        'rating': r.rating,
        'content': r.content,
        'imagePath': r.imagePath,
        'dishID': r.dishID,  # foreign key
        'restaurantID': r.restaurantID  # foreign key
    } for r in reviews]

    # fetch saved dishes
    saved_dishes = SavedDishes.query.all()
    data['saved_dishes'] = [{
        'userID': sd.userID,  # primary key (foreign key)
        'dishID': sd.dishID,  # primary key (foreign key)
        'dateSaved': sd.dateSaved
    } for sd in saved_dishes]

    # fetch saved restaurants
    saved_restaurants = SavedRestaurants.query.all()
    data['saved_restaurants'] = [{
        'userID': sr.userID,  # primary key (foreign key)
        'restaurantID': sr.restaurantID,  # primary key (foreign key)
        'dateSaved': sr.dateSaved
    } for sr in saved_restaurants]

    # fetch taste buddies
    taste_buddies = TasteBuddies.query.all()
    data['taste_buddies'] = [{
        'userID': tb.userID,  # primary key (foreign key)
        'buddyID': tb.buddyID,  # primary key (foreign key)
        'dateAdded': tb.dateAdded
    } for tb in taste_buddies]

    # fetch menus
    menus = Menu.query.all()
    data['menus'] = [{
        'menuID': m.menuID,  # primary key
        'menuName': m.menuName,
        'lastUpdated': m.lastUpdated
    } for m in menus]

    # fetch operating hours
    operating_hours = OperatingHours.query.all()
    data['operating_hours'] = [{
        'operatingHoursID': oh.operatingHoursID,  # primary key
        'daysOfWeek': oh.daysOfWeek,
        'openTime': oh.openTime,
        'closeTime': oh.closeTime
    } for oh in operating_hours]

    return render_template('test_database.html', tables_data=data)
