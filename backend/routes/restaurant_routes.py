from flask import Blueprint, render_template


restaurant_bp = Blueprint('restaurant', __name__)



@restaurant_bp.route("/restaurant/<int:restaurant_id>")
def restaurant_detail(restaurant_id):
    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return "Restaurant not found", 404
    
    dishes_with_match = [
        {
            "name": dish.name,
            "price": dish.price,
            "image_url": dish.image_url,
            "match_percentage": calculate_match_percentage(user, dish), # not sure how we're actually calculating this, dummy variable
        }
        for dish in restaurant.dishes
    ]
    
    # Sort in descending order
    sorted_dishes = sorted(restaurant.dishes, key=lambda dish: dish.match_percentage, reverse=True)
    
    return render_template("restaurant_detail.html", restaurant=restaurant, dishes=sorted_dishes)
