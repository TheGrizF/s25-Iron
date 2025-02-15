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

@daily_dish_bp.route('/TasteBuds.html')
def TasteBuds():
    return render_template('TasteBuds.html')

@daily_dish_bp.route('/restaurant/<id>')
def restaurant_detail(id):
    return render_template('restaurant_detail.html')
    
