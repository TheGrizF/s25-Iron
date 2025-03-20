from flask import Blueprint, render_template, session
from database import db
from backend.utils import get_dish_info, get_dish_recommendations

dish_bp = Blueprint('dish', __name__)

@dish_bp.route("/dishes")
def dishes():
    user_id = session.get("user_id")
    if not user_id:
        return "Must be logged in!", 404
    
    dish_recommendations = get_dish_recommendations(user_id)
    dish_scores = {d[0]: d[2] for d in dish_recommendations}
    session["dish_scores"] = dish_scores

    dishes = [
        get_dish_info(d[0])
        for d in dish_recommendations
    ]

    return render_template("dishes.html", dishes = dishes)

@dish_bp.route("/dishes/<int:dish_id>")
def dish_detail(dish_id):

    user_id = session.get('user_id')        
    if not user_id:
        return "User not logged in", 404

    dish_info = get_dish_info(dish_id, include_reviews=True)

    return render_template("dish_detail.html", dish = dish_info )
