from flask import Blueprint, render_template, session, request, jsonify
from database import db
from backend.utils import get_dish_info, get_dish_recommendations
from database.models.user import savedDishes

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

@dish_bp.route("/toggle-save/<int:dish_id>", methods=["POST"])
def toggle_save(dish_id):
    user_id = session.get("user_id")
     
    if not user_id:
        return jsonify({"success": False, "message": "User not logged in"}), 401

    
    saved_dish = savedDishes.query.filter_by(user_id=user_id, dish_id=dish_id).first()

    if saved_dish:
        db.session.delete(saved_dish)
        saved = False
    else:
        new_save = savedDishes(user_id=user_id, dish_id=dish_id)
        db.session.add(new_save)
        saved = True

    db.session.commit()
    return jsonify({"success": True, "saved": saved})