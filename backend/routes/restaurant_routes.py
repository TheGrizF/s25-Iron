from flask import Blueprint, json, render_template, session, request, flash, redirect, url_for
from database import db
from database.models.restaurant import operatingHours, restaurant,liveUpdate
from database.models.dish import dish, menu, menuDishJunction
from database.models.user import user
from backend.utils import get_all_restaurant_info, get_dish_recommendations, get_restaurant_info, get_restaurant_dish_scores, relative_time
from better_profanity import profanity

restaurant_bp = Blueprint('restaurant', __name__)

@restaurant_bp.route("/restaurants")
def restaurants():
    user_id = session.get("user_id")
    if not user_id:
        flash("Log in to view restaurants!", "error")
        return redirect(url_for("auth.login"))

    
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
        flash("Log in to view restaurant info!", "error")
        return redirect(url_for("auth.login"))

    rest = restaurant.query.get(restaurant_id)
    restaurant_info = get_restaurant_info(user_id, rest)
    if not restaurant_info:
        return "Restaurant not found", 404
    
    sorted_dishes = get_restaurant_dish_scores(user_id, restaurant_id)

    # get live updates for this restaurant
    live_updates_raw = (
        db.session.query(liveUpdate)
        .filter(liveUpdate.restaurant_id == restaurant_id)
        .order_by(liveUpdate.created_at.desc())
        .all()
    )

    live_updates = []
    for update in live_updates_raw:
        live_updates.append({
        "update_content": update.update_content,
        "time": relative_time(update.created_at),
        "user_name": f"{update.user.first_name} {update.user.last_name}",
        "icon": update.user.icon_path
    })
    session[f'restaurant_{restaurant_id}_dishes'] = json.dumps(sorted_dishes)  # store in flask session to reuse and limit db calls?

    return render_template("restaurant_detail.html", restaurant=restaurant_info, dishes=sorted_dishes, updates=live_updates)

@restaurant_bp.route("/restaurant/<int:restaurant_id>/menu")
def view_menu(restaurant_id):

    """
    The function displays the menu for a specific restaurant.
    It also checks if the user is logged in the session. 
    If the user is not logged in, it shows an error message and redirects them to the login page. 

    Returns:
        It returns a redirect to the login page if the user is not logged in. 

    """
    user_id = session.get("user_id")
    if not user_id:
        flash("Log in to view menus!", "error")
        return redirect(url_for("auth.login"))

    
    this_restaurant = restaurant.query.get(restaurant_id)
    if not this_restaurant:
        return "Restaurant not found", 404
    
    recall_dishes = session.get(f'restaurant_{restaurant_id}_dishes')
    if recall_dishes:
        sorted_dishes = json.loads(recall_dishes)
    else:
        print('storing dishes in json failed')
        sorted_dishes = get_restaurant_dish_scores(user_id, restaurant_id)
    
    return render_template("view_menu.html", restaurant=this_restaurant, dishes=sorted_dishes)

@restaurant_bp.app_template_filter('truncate_at_comma')
def register_truncate_filter(text):
    return truncate_at_comma(text)

# function to truncate at comma, specifically for addresses
def truncate_at_comma(text):
    if ',' in text:
        return text.split(',')[1]
    return text

def sort_restaurants(filtered_restaurants, sort_by="match_percentage"):
    """
    Sorts the restaurants based on the selected criteria.
    :param filtered_restaurants: List of restaurant information.
    :param sort_by: The key to sort by (default is 'match_percentage').
    :return: Sorted list of restaurants.
    totally chatgpt, can you tell?
    """
    # Define the sort key
    if sort_by == "match_percentage":
        return sorted(filtered_restaurants, key=lambda r: r["match_percentage"], reverse=True)
    elif sort_by == "name":
        return sorted(filtered_restaurants, key=lambda r: r["restaurant_name"].lower()) 
    else:
        return filtered_restaurants 


@restaurant_bp.route('/restaurant/<int:restaurant_id>/post-update', methods=['POST'])
def post_update(restaurant_id):

    """
    This function handles the posting of a live update for a specific restaurant by a logged-in user.
    This function processes a form submission from a user, validates the content written,
    checks for profanity, and saves the update to the database.
    It ensures the user is authenticated before allowing the action.

    Returns:
        It returns a redirect response to the login page if the user is not logged in,
        or if the user is logged in it returns back to the restaurant detail page with messages indicating success or error with the live post update.

    """
    
    profanity.load_censor_words()
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to post an update.', 'error')
        return redirect(url_for('auth.index'))

    update_content = request.form.get('update_content', '').strip()

    if not update_content:
        flash('Update cannot be empty.', 'error')
        return redirect(url_for('restaurant.restaurant_detail', restaurant_id=restaurant_id))


    if profanity.contains_profanity(update_content):
        flash('Your update contains inappropriate language.', 'error')
        return redirect(url_for('restaurant.restaurant_detail', restaurant_id=restaurant_id))


    new_update = liveUpdate(
        restaurant_id=restaurant_id,
        user_id=user_id,
        update_content=update_content
    )
    db.session.add(new_update)
    db.session.commit()
    flash('Your update has been posted.', 'success')
    return redirect(url_for('restaurant.restaurant_detail', restaurant_id=restaurant_id))
