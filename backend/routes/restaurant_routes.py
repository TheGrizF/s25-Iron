from flask import Blueprint, render_template, session
from database import db
from database.models.restaurant import restaurant
from database.models.dish import dish, menu, menuDishJunction
from backend.utils import get_dish_recommendations

restaurant_bp = Blueprint('restaurant', __name__)

@restaurant_bp.route("/restaurant/<int:restaurant_id>")
def restaurant_detail(restaurant_id):

    user_id = session.get('user_id')        # gets user_id for current user in session
    if not user_id:
        return "User not logged in", 404
    
    this_restaurant: restaurant = restaurant.query.get(restaurant_id)
    if not this_restaurant:
        return "Restaurant not found", 404
    
    # Get dishes at the restaurant
    restaurant_dishes = (
        db.session.query(dish)
        .join(menuDishJunction, dish.dish_id == menuDishJunction.dish_id)
        .join(menu, menu.menu_id == menuDishJunction.menu_id)
        .filter(menu.restaurant_id == restaurant_id)
        .all()
    )
    # List to Set
    restaurant_dishes = {d[0] for d in restaurant_dishes}

    # Get list of user dish percentages
    user_dish_matches = get_dish_recommendations(user_id)  # [0] = dish_id, [1] = buddy_id, [2] = % match

    # Filter list to combine the two
    matched_dishes = [d[0] for d in user_dish_matches if d[0] in restaurant_dishes]

    # Run some query to get data
    dish_data = {
        d.dish_id: dishes_with_match
        for d in db.session.query(dish).filter(dish.dish_id.in_(matched_dishes)).all()
    }

    # Filters user dishes and adds all info to this list
    dishes_with_match = [
        {
            "dish_id": d[0],
            "name": dish_data[d[0]].dish_name,
            "price:": dish_data[d[0]].price,
            "image_url": dish_data[d[0]].image_path,
            "match_percentage": d[2],
            "available": dish_data[d[0]].available,
            "featured": dish_data[d[0]].featured,
        }
        for d in user_dish_matches if d[0] in dish_data
    ]

    restaurant_info = {
        "restaurant_id": this_restaurant.restaurant_id,
        "name": this_restaurant.restaurant_name,
        "rating": this_restaurant.rating_average,
        "busy": this_restaurant.busy_average,
        "clean": this_restaurant.clean_average,
        "description": this_restaurant.description,
        "image_path": this_restaurant.image_path,
        "phone": this_restaurant.phone_number,
        "hours": this_restaurant.operating_hours, #this one might not work right...
    }

    # Sort in descending order
    sorted_dishes = sorted(dishes_with_match, key=lambda d: d["match_percentage"], reverse=True)
    
    return render_template("restaurant_detail.html", restaurant=restaurant_info, dishes=sorted_dishes)