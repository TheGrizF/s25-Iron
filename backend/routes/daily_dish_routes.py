from flask import Blueprint, render_template


daily_dish_bp = Blueprint('daily_dish', __name__)

@daily_dish_bp.route('/dailyDish')
def daily_dish():
    return render_template('dailyDish.html')

@daily_dish_bp.route('/search')
def search():
    return render_template('search.html')

@daily_dish_bp.route('/restaurants')
def restaurants():
    return render_template('restaurants.html')

@daily_dish_bp.route('/restaurant/<id>')
def restaurant_detail(id):
    return render_template('restaurant_detail.html')

@daily_dish_bp.route('/database')
def database():
    return render_template('database.html')

@daily_dish_bp.route('/test_database')
def test_database():
    from database import db
    from database.models import User

    data = {}
    users = User.query.all()
    data['users'] = [{'firstName': u.firstName, 'lastName': u.lastName, 'email': u.email} for u in users]

    return render_template('test_database.html', tables_data=data)