from flask import Blueprint, redirect, render_template, session, request, jsonify, url_for, flash, render_template_string
from database import db
from backend.utils import get_dish_info, get_dish_recommendations, get_filtered_sorted_dishes
from database.models.review import review
from database.models.user import savedDishes, user


dish_bp = Blueprint('dish', __name__)

@dish_bp.route("/dishes")
def dishes():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in first!", "error")
        return redirect(url_for("auth.login"))

    # grab query params
    sort_by = request.args.get('sort', 'match_score')
    filter_by = request.args.get('filter', 'all')
    search = request.args.get('search', "")

    # get full filtered/sorted dish list (shared with /load-more-dishes)
    all_dishes = get_filtered_sorted_dishes(user_id, search, filter_by, sort_by)

    # debug output (optional)
    import os, json
    os.makedirs("debug_logs", exist_ok=True)
    with open("debug_logs/debug_dishes.json", "w") as f:
        json.dump(all_dishes, f, indent=2, default=str)

    # only send first 20 for initial load
    return render_template("dishes.html", dishes=all_dishes[:20])

@dish_bp.route("/dishes/<int:dish_id>")
def dish_detail(dish_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in first!", "error")
        return redirect(url_for("auth.login"))

    dish_info = get_dish_info(dish_id, include_reviews=True)
    is_saved = savedDishes.query.filter_by(user_id=user_id, dish_id=dish_id).first() is not None
    dish_info["is_saved"] = is_saved

    return render_template("dish_detail.html", dish=dish_info, is_saved=is_saved)


@dish_bp.route("/submit-review", methods=["POST"])
def submit_review():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in first!", "error")
        return redirect(url_for("auth.login"))
    dish_id = request.form.get("dish_id")
    restaurant_id = request.form.get("restaurant_id")
    rating = request.form.get("rating")
    content = request.form.get("content")
    rating = int(rating)

    new_review = review(
        user_id=user_id,
        dish_id=dish_id,
        restaurant_id=restaurant_id,
        rating=rating,
        content=content
    )
    db.session.add(new_review)
    db.session.commit()

    return redirect(url_for('dish.dish_detail', dish_id=dish_id))


@dish_bp.route("/review", methods=["GET"])
def review_page():
    dish_id = request.args.get("dish_id")
    restaurant_id = request.args.get("restaurant_id")
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in first!", "error")
        return redirect(url_for("auth.login"))
    user_obj = user.query.get(user_id)
    return render_template("review.html", dish_id=dish_id, restaurant_id=restaurant_id, user=user_obj)


@dish_bp.route("/toggle-save/<int:dish_id>", methods=["POST"])
def toggle_save(dish_id):
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in first!", "error")
        return redirect(url_for("auth.login"))

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

@dish_bp.route("/load-more-dishes")
def load_more_dishes():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Not logged in"}), 403

    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", 20))

    sort_by = request.args.get("sort", "match_score")
    filter_by = request.args.get("filter", "all")
    search = request.args.get("search", "")

    all_dishes = get_filtered_sorted_dishes(user_id, search, filter_by, sort_by)
    paginated = all_dishes[offset:offset + limit]

    html = ""
    for dish in paginated:
        html += render_template("components/dish_card.html", dish=dish)

    return jsonify({
        "success": True,
        "dish_html": html,
        "count": len(paginated),
        "has_more": offset + limit < len(all_dishes)
    })
