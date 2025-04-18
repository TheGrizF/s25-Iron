from flask import Blueprint, redirect, render_template, session, request, jsonify, url_for
from database import db
from backend.utils import get_dish_info, get_dish_recommendations
from database.models.review import review
from database.models.user import savedDishes, user

dish_bp = Blueprint('dish', __name__)

@dish_bp.route("/dishes")
def dishes():
    user_id = session.get("user_id")
    if not user_id:
        return "Must be logged in!", 404
    
    dish_recommendations = get_dish_recommendations(user_id)
    dish_scores = {d[0]: d[2] for d in dish_recommendations}
    session["dish_scores"] = dish_scores

    # to load saved dishes!
    saved_dish_ids = {
        saved.dish_id for saved in savedDishes.query.filter_by(user_id=user_id).all()
    }

    dishes = []
    for d in dish_recommendations:
        info = get_dish_info(d[0])
        if info is not None:
            info["is_saved"] = d[0] in saved_dish_ids
            dishes.append(info)

    sort_by = request.args.get('sort', 'match_score') #default is match score
    filter_by = request.args.get('filter','all')

    # Searching logic
    search = request.args.get('search', "").lower()
    exclude_words = {'the', 'a', 'and'}
    searched_keywords = [word for word in search.split() if word not in exclude_words]

    # Sorting and filtering arguments
    filtered_dishes = dishes.copy()

    if filter_by != 'all':
        if filter_by == "four_stars":
            filtered_dishes = [d for d in dishes if 4.0 <= d["average_rating"] <= 5.0]
        elif filter_by == "three_stars":
            filtered_dishes = [d for d in dishes if 3.0 <= d["average_rating"] < 4.0]
        elif filter_by == "two_stars":
            filtered_dishes = [d for d in dishes if 2.0 <= d["average_rating"] < 3.0]
        elif filter_by == "one_star":
            filtered_dishes = [d for d in dishes if 1.0 <= d["average_rating"] < 2.0]
        elif filter_by == "saved":
            saved_dish_ids = {d.dish_id for d in savedDishes.query.filter_by(user_id=user_id).all()}
            filtered_dishes = [d for d in dishes if d["dish_id"] in saved_dish_ids]


    # Search logic continued to remain within filtered constraints
    if searched_keywords:
        filtered_dishes = [
            d for d in filtered_dishes if any(
                keyword in d['dish_name'].lower() or
                keyword in d['restaurant_name'].lower() or
                keyword in d['description'].lower()          
                for keyword in searched_keywords
            )
        ]   

    sorted_dishes = sort_dishes(filtered_dishes, sort_by)

    return render_template("dishes.html", dishes = sorted_dishes)

@dish_bp.route("/dishes/<int:dish_id>")
def dish_detail(dish_id):

    user_id = session.get('user_id')        
    if not user_id:
        return "User not logged in", 404

    dish_info = get_dish_info(dish_id, include_reviews=True)

    is_saved = savedDishes.query.filter_by(user_id=user_id, dish_id=dish_id).first() is not None

    dish_info["is_saved"] = is_saved

    return render_template("dish_detail.html", dish = dish_info, is_saved=is_saved)

@dish_bp.route("/submit-review", methods=["POST"])
def submit_review():
    user_id = session.get('user_id')

    dish_id = request.form.get("dish_id")
    restaurant_id = request.form.get("restaurant_id")
    rating = request.form.get("rating")
    content = request.form.get("content")
    print(dish_id)
    rating = int(rating)
    
    new_review = review(
        user_id = user_id,
        dish_id = dish_id,
        restaurant_id = restaurant_id,
        rating = rating,
        content = content
    )
    print("dishid = ", repr(dish_id))
    db.session.add(new_review)
    db.session.commit()

    return redirect(url_for('dish.dish_detail', dish_id=dish_id))

@dish_bp.route("/review", methods=["GET"])
def review_page():
    dish_id = request.args.get("dish_id")
    restaurant_id = request.args.get("restaurant_id")
    user_id = session.get("user_id")
    user_obj = user.query.get(user_id)
    return render_template("review.html", dish_id=dish_id, restaurant_id=restaurant_id, user=user_obj)

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

def sort_dishes(filtered_dishes, sort_by="match_score"):
    if sort_by == "match_score":
        return sorted(filtered_dishes, key=lambda d: d["match_score"], reverse=True)
    elif sort_by == "name":
        return sorted(filtered_dishes, key=lambda d: d["dish_name"].lower()) 
    elif sort_by == "price":
        return sorted(filtered_dishes, key=lambda d: float(d["price"]))
    elif sort_by == "restaurant_name":
        return sorted(filtered_dishes, key=lambda d : d["restaurant_name"])
    else:
        return filtered_dishes 