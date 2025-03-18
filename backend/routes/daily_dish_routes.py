from flask import Blueprint, render_template, session
from database import db
from database.models.dish import dish
from backend.utils import get_featured_dishes, get_daily_dishes
daily_dish_bp = Blueprint('daily_dish', __name__)

@daily_dish_bp.route('/dailyDish')
def daily_dish():
    user_id = session.get('user_id')
    if not user_id:
        return "Not Logged In", 404
    

    featured_dishes = get_featured_dishes()
    recommended_dishes = get_daily_dishes(user_id, 10)

    return render_template('dailyDish.html', featured_dishes=featured_dishes, recommended_dishes=recommended_dishes)

# Get Featured dishes from restaurants to display in carosel - sort by rating
# top 10?
def get_featured_dishes():
    
    featured = (
        db.session.query(dish)
        .filter(dish.featured.is_(True))
        .all()
    )
    
    featured_dish_info = [
        {
            "dish_id": dish.dish_id,
            "name": dish.dish_name,
            "image": dish.image_path,
            "restaurant": dish.menu_dishes[0].menu.restaurant.restaurant_name
        }
        for dish in featured
    ]
    
    return featured_dish_info

@daily_dish_bp.route('/search')
def search():
    return render_template('search.html')

@daily_dish_bp.route('/TasteBuds.html')
def TasteBuds():
    return render_template('TasteBuds.html')

@daily_dish_bp.route('/restaurant/<id>')
def restaurant_detail(id):
    return render_template('restaurant_detail.html')

@daily_dish_bp.route('/review', methods=['GET', 'POST'])
def review():
    user = {'firstName': 'Person-I-Know'} #Umm, don't know how to connect it with db right now
    return render_template('review.html', user = user)
