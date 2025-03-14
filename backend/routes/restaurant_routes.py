from flask import Blueprint, render_template, session
from database import db
from database.models.restaurant import operatingHours, restaurant
from database.models.dish import dish, menu, menuDishJunction
from backend.utils import get_all_restaurant_info, get_dish_recommendations, get_restaurant_info, get_restaurant_dish_scores

restaurant_bp = Blueprint('restaurant', __name__)

@restaurant_bp.route("/restaurants")
def restaurants():
    user_id = session.get("user_id")
    if not user_id:
        return "Must be logged in!", 404
    
    restaurant_info = get_all_restaurant_info(user_id)

    sorted_restaurants = sorted(restaurant_info, key=lambda r: r["match_percentage"], reverse=True)

    return render_template("restaurants.html", restaurants=sorted_restaurants)

@restaurant_bp.route("/restaurant/<int:restaurant_id>")
def restaurant_detail(restaurant_id):

    user_id = session.get('user_id')        # gets user_id for current user in session
    if not user_id:
        return "User not logged in", 404
    
    restaurant_info = get_restaurant_info(user_id, restaurant_id)
    if not restaurant_info:
        return "Restaurant not found", 404
    
    sorted_dishes = get_restaurant_dish_scores(user_id, restaurant_id)
    return render_template("restaurant_detail.html", restaurant=restaurant_info, dishes=sorted_dishes)