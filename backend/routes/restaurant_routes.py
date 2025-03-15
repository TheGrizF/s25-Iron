from flask import Blueprint, render_template, session, request
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

    sort_by = request.args.get('sort', 'match_percentage') #default is match percentage
    filter_by = request.args.get('filter','all')
    
    # Searching logic
    search = request.args.get('search', "").lower()
    exclude_words = {'the', 'a', 'and'}
    searched_keywords = [word for word in search.split() if word not in exclude_words]


    
    # Sorting and filtering arguments
    filtered_restaurants = restaurant_info

    if filter_by != 'all':
        filtered_restaurants = [r for r in restaurant_info if r['cuisine'] == filter_by]
        
    sorted_restaurants = sort_restaurants(filtered_restaurants, sort_by)

    # Search logic continued to remain within filtered constraints
    if searched_keywords:
        sorted_restaurants = [
            r for r in filtered_restaurants if any(
                keyword in r['restaurant_name'].lower() or
                keyword in r['cuisine'].lower() or
                any(keyword in dish['name'].lower() for dish in r['dishes'])          
                for keyword in searched_keywords
            )
        ]

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

@restaurant_bp.app_template_filter('truncate_at_comma')
def register_truncate_filter(text):
    return truncate_at_comma(text)


# function to truncate at comma, specifically for addresses
def truncate_at_comma(text):
    if ',' in text:
        return text.split(',')[0]
    return text



def sort_restaurants(filtered_restaurants, sort_by="match_percentage"):
    """
    Sorts the restaurants based on the selected criteria.
    :param filtered_restaurants: List of restaurant information.
    :param sort_by: The key to sort by (default is 'match_percentage').
    :return: Sorted list of restaurants.
    """
    # Define the sort key
    if sort_by == "match_percentage":
        return sorted(filtered_restaurants, key=lambda r: r["match_percentage"], reverse=True)
    elif sort_by == "name":
        return sorted(filtered_restaurants, key=lambda r: r["restaurant_name"].lower()) 
    else:
        return filtered_restaurants 