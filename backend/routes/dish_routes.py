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

    # # debug output
    # import os, json
    # os.makedirs("debug_logs", exist_ok=True)
    # with open("debug_logs/debug_dishes.json", "w") as f:
    #     json.dump(all_dishes, f, indent=2, default=str)

    # only send first 20 for initial load
    return render_template("dishes.html", dishes=all_dishes[:20])

@dish_bp.route("/dishes/<int:dish_id>")
def dish_detail(dish_id):

    """
    The function displays detailed information about a specific dish, including reviews and save status.
    This function ensures the user is logged in before retrieving dish details from the database.
    It checks whether the dish has been saved by the user and passes this information along with
    the dish data to the template for rendering.

    Parameter:
        dish_id: The unique identifier of the dish to display.

    Returns:
        Renders the 'dish_detail.html' template with the dish information and saved status.
        If the user is not logged in, redirects to the login page with a message.
        
    """
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

    """
    This function handles the submission of a user review for a dish.
    The function ensures the user is logged in, retrieves the submitted form
    for the dish review (including the dish ID, restaurant ID, rating, and review content).
    It also creates a new review record, stores it in the database, and redirects the user to the
    dish detail page.

    Returns:
        Redirects the user to the dish detail page after successfully saving the review.
        If the user is not logged in, redirects them to the login page with a message.

    """
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

    """
    The function renders the review page for a specific dish and restaurant.
    This function checks if the user is logged in. If not, it redirects them to the login page.
    If the user is authenticated, it retrieves the dish ID, restaurant ID and the user object from the database.
    It also displays the review submission page.

    Returns:
        It returns the 'review.html' template with the dish ID, restaurant ID, and user object 
        if the user is authenticated. If not, it redirects the user to the login page with an error message.

    """
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

    """

    This function toggles the saved status of a dish for the currently logged-in user.
    If the user is not logged in, they are redirected to the login page. If the dish is not currently saved, the dish 
    is added to their saved list. 

    Returns:
        It returns A JSON object indicating the success status and the new saved state 
        (True if saved, False if unsaved), or a redirect response if the user is not logged in.

    """
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

    """

    This function loads additional dishes for the user based on optional search, filter, and parameters.
    Dishes are filtered and sorted based on the parameters.
    The user must be logged in to access this functionality.

    """
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
