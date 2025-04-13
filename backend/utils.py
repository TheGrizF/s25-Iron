"""
Use this to create all the helper functions for the routes.
Keeps them organized so we can use them again if we need to.
"""
from datetime import datetime, timedelta
from flask import session
from sqlalchemy import func
from database import db
from database.models.taste_profiles import dishTasteProfile
from database.models.user import cuisineUserJunction, savedDishes, user, user_allergen, user_restriction, tasteComparisons, friends
from database.models.review import review
from database.models.dish import dish, dish_allergen, dish_restriction, menu, menuDishJunction
from database.models.restaurant import liveUpdate, restaurant

def get_live_updates(user_id, threshold=75):
    """
    Gets a list of the most recent updates for restaurants that match a threshold for the user

    :param user_id: id of user to base threshold for
    :param threshold: only restaurants above this % match will be returned
    :return: Sorted list of restaurants dictionaries and their updates
    """

    all_restaurants = get_all_restaurant_info(user_id)
    match_rest_ids = [
        rest['restaurant_id'] for rest in all_restaurants
        if rest.get('match_percentage', 0) >= threshold
    ]

    if not match_rest_ids:
        return []
    
    match_updates = (
        db.session.query(liveUpdate)
        .filter(liveUpdate.restaurant_id.in_(match_rest_ids))
        .filter(liveUpdate.user_id != user_id)
        .order_by(liveUpdate.created_at.desc())
        .all()
    )

    live_updates = []
    for update in match_updates:
        user_name = f"{update.user.first_name} {update.user.last_name}"
        live_updates.append({
            "restaurant_id": update.restaurant.restaurant_id,
            "restaurant_name": update.restaurant.restaurant_name,
            "content": update.update_content,
            "time_posted": relative_time(update.created_at),
            "user_name": user_name,
        })

    return live_updates

def get_dish_info(dish_id, include_reviews=False):
    """
    Gets all the information for a dish based on its dish_id.
    optional 'include_reviews' will additionally include a list of review information

    dish_id - dish id
    dish_name - Name of dish
    image - path to image
    match_score - taste match score for current user
    average_rating - average rating based on all reviews
    restaurant_id - restaurant id
    restaurant_name - name of restaurant
    description - dish description
    price - price per dish (usd)
    allergens - list of dish allergens
    restrictions - list of diets that this dish is acceptable for
    available - Boolean, false if dish is 86'd

    when include_reviews is true, dictionary will include:
    reviews: a list of reviews for the dish including:
    user_name - user name as string First Last
    user_icon - path to user image
    content - review text
    rating - rating the user gave
    time_stamp - date review was left
    """

    dish_info = db.session.query(dish).get(dish_id)
    if not dish_info:
        return None
    
    # Calculate Average Rating
    average_rating = (
        db.session.query(db.func.avg(review.rating))
        .filter(review.dish_id == dish_id)
        .scalar()
    ) or 0

    # Create allergen and restriction lists
    allergens = [a.allergen.lower() for a in dish_info.dish_allergens]
    restrictions = [r.restriction.lower() for r in dish_info.dish_restrictions]

    review_list = []
    if include_reviews:
        reviews = (
            db.session.query(review)
            .filter(review.dish_id == dish_id, review.user_id != session.get("user_id"))
            .order_by(review.created_at.desc())
            .all()
        )
        review_list = [
            {
                "user_name": f"{rev.user.first_name} {rev.user.last_name}",
                "user_icon": rev.user.icon_path,
                "content": rev.content,
                "rating": rev.rating,
                "time_stamp": relative_time(rev.created_at),
            }
            for rev in reviews
        ]

    dish_scores = session.get("dish_scores", {})
    if not dish_scores:
        dish_recommendations = get_dish_recommendations(session.get("user_id"))
        dish_scores = {d[0]: d[2] for d in dish_recommendations}
        session["dish_scores"] = dish_scores

    return {
        "dish_id": dish_info.dish_id,
        "dish_name": dish_info.dish_name,
        "image": dish_info.image_path,
        "match_score": dish_scores.get(dish_id, 42),
        "average_rating": round(average_rating, 1),
        "restaurant_id": dish_info.menu_dishes[0].menu.restaurant.restaurant_id,
        "restaurant_name": dish_info.menu_dishes[0].menu.restaurant.restaurant_name,
        "restaurant_address": dish_info.menu_dishes[0].menu.restaurant.location,
        "description": dish_info.description,
        "price": dish_info.price,
        "allergens": allergens,
        "restrictions": restrictions,
        "available": dish_info.available,
        "reviews": review_list,
        
    }

# Get Featured dishes from restaurants to display in carosel - sort by rating
# top 10?
def get_featured_dishes():
    
    featured = (
        db.session.query(dish)
        .filter(dish.featured.is_(True))
        .all()
    )
    
    featured_dish_info = [
        {
            "dish_id": dish.dish_id,
            "name": dish.dish_name,
            "image": dish.image_path,
            "restaurant": dish.menu_dishes[0].menu.restaurant.restaurant_name,
            "restaurant_id": dish.menu_dishes[0].menu.restaurant.restaurant_id,
        }
        for dish in featured
    ]
    
    return featured_dish_info

def get_daily_dishes(user_id, limit=10):
    """
    Get dishes with scores where the score didn't come from user reviews
    should be dishes user hasn't tried yet
    """

    recommended = get_dish_recommendations(user_id)
    
    new_dishes = [dish for dish in recommended if dish[1] != user_id][:limit]

    dish_ids = [dish[0] for dish in new_dishes]
    dishes = {
        this_dish.dish_id: this_dish 
        for this_dish in db.session.query(dish).filter(dish.dish_id.in_(dish_ids)).all()
    }

    reviews = (
        db.session.query(review)
        .filter(review.dish_id.in_(dishes.keys()), review.user_id != user_id)
        .order_by(review.created_at.desc())
        .distinct(review.dish_id)
        .all()
    )

    buddy_reviews = {
        rev.dish_id: {
            "buddy_name": f"{rev.user.first_name} {rev.user.last_name}",
            "buddy_icon": rev.user.icon_path,
            "review_content": rev.content,
            "time_stamp": relative_time(rev.created_at),
            "rating": rev.rating,
        }
        for rev in reviews
    }
    
    daily_dishes = [
        {
            "dish_id": id,
            "name": dishes[id].dish_name,
            "image_path": dishes[id].image_path,
            "restaurant": dishes[id].menu_dishes[0].menu.restaurant.restaurant_name,
            "restaurant_id": dishes[id].menu_dishes[0].menu.restaurant.restaurant_id,
            "match_score": score,

            "buddy_name": buddy_reviews[id]["buddy_name"],
            "buddy_icon": buddy_reviews[id]["buddy_icon"],
            "buddy_rating": buddy_reviews[id]["rating"],
            "review_content": buddy_reviews[id]["review_content"],
            "time_stamp": buddy_reviews[id]["time_stamp"]
        }
        for id, _, score in new_dishes if id in dishes
    ]
        
    return daily_dishes

def get_friend_reviews(user_id, limit=5):
    """
    Gets a list of the recent reviews from the user's friends.
    Dictionary return contains:
    -friend_name: friends full name
    -friend_icon: user icon of the friend
    -dish_name: name of dish they reviewed
    -dish_id: dish id to link to dish page
    -retaurant_name: name of restaurant where dish is
    -restaurant_id: to link to restaurant page
    -content: the written review
    -rating: the score the user gave
    """
    friend_ids = [
        f[0] for f in db.session.query(friends.buddy_id)
        .filter(friends.user_id == user_id)
        .all()
    ]
    
    # Early exit if user doesn't follow anyone
    if not friend_ids:
        return []
    
    # Reviews from friends in descending order
    raw_reviews = (
        db.session.query(review)
        .filter(review.user_id.in_(friend_ids))
        .order_by(review.created_at.desc())
        .all()
    )

    # Filter 1 per friend, most recent    
    remove_duplicates = {}
    for rev in raw_reviews:
        if rev.user_id not in remove_duplicates:
            remove_duplicates[rev.user_id] = rev
    
    friend_reviews=[]
    for rev in remove_duplicates.values():
        friend_reviews.append({
            "friend_id": rev.user_id,
            "friend_name": f"{rev.user.first_name} {rev.user.last_name}",
            "friend_icon": rev.user.icon_path,
            "content": rev.content,
            "rating": rev.rating,
            "dish_id": rev.dish_id,
            "dish_name": rev.dish.dish_name,
            "restaurant_id": rev.dish.menu_dishes[0].menu.restaurant.restaurant_id,
            "restaurant_name": rev.dish.menu_dishes[0].menu.restaurant.restaurant_name,
            "time_stamp": relative_time(rev.created_at),
        })
    
    return friend_reviews[:limit]

def get_saved_dishes(user_id):
    """
    Compiles a list of the users saved dishes with oldest first
    saved in dictionary containing:
        -dish_name: name of dish they reviewed
        -dish_id: dish id to link to dish page
        -image: path to dish image
        -retaurant_name: name of restaurant where dish is
        -restaurant_id: to link to restaurant page
        -date_saved: date user saved the dish
    """
    user_info = db.session.query(user).get(user_id)

    if not user_info:
        return []
    
    saved_dishes = []
    for saved in user_info.saved_dishes:
        user_dish = saved.dish

        saved_dishes.append({
            "dish_id": user_dish.dish_id,
            "dish_name": user_dish.dish_name,
            "image": user_dish.image_path,
            "restaurant_name": user_dish.menu_dishes[0].menu.restaurant.restaurant_name,
            "restaurant_id": user_dish.menu_dishes[0].menu.restaurant.restaurant_id,
            "date_saved": saved.date_saved.strftime("%B %d, %Y"),
        })
    
    return saved_dishes

def get_dish_recommendations(user_id):
    """
    Method to determine a list of dishes with appropriate score
    :param user_id: user_id to get curated list of dishes to try
    :return scored_matches: list of tuples containing (dish_id, tastebuddy_id, dish_score)
        dish_id: id of the dish to recommend to user
        bud_id: user_id of the taste match profile that reviewed dish
        dish_score: % score based on average rating, taste buddy score, and cuisine match, 
    """
    # Get user info from db
    user_tp = db.session.query(user).filter(user.user_id == user_id).first()
    user_allergy = db.session.query(user_allergen.allergen).filter(user_allergen.user_id == user_id).all()
    user_dietary = db.session.query(user_restriction.restriction).filter(user_restriction.user_id == user_id).all()
    user_cuisine = db.session.query(cuisineUserJunction).filter(cuisineUserJunction.user_id == user_id).all()

    # make lists (if aplicable)
    user_allergy_list = {a[0].lower() for a in user_allergy}
    user_dietary_list = {r[0].lower() for r in user_dietary}
    user_cuisine_list = {c.cuisine_id: c.preference_level for c in user_cuisine}

    # Get top 6 taste matches  --- commented out limit, get them all?
    taste_bud_query = (
        db.session.query(tasteComparisons.compare_to, tasteComparisons.comparison_num)
        .filter(tasteComparisons.compare_from == user_id)
        .order_by(tasteComparisons.comparison_num.asc())
        #.limit(10)
        .all()
    )
    # t[0]:t[1] => buddy_id & comparison_num
    taste_bud_id = {t[0]: t[1] for t in taste_bud_query}

    # Top 3 dishes from each match  --- commented out, get them all?
    unique_dishes = {}
    for bud_id, comparison_num in taste_bud_id.items():
        best_dish_query = (
            db.session.query(review.dish_id, review.rating)
            .filter(review.user_id == bud_id)
            .order_by(review.rating.desc())
            #.limit(3)
            .all()
        )

        # check for duplicates
        for dish_id, bud_review in best_dish_query:
            if dish_id not in unique_dishes or bud_review > unique_dishes[dish_id][2]:
                unique_dishes[dish_id] = (bud_id, comparison_num, bud_review)

    # include users own reviews!
    user_reviews = (
        db.session.query(review.dish_id, review.rating)
        .filter(review.user_id == user_id)
        .all()
    )
    
    for dish_id, user_review in user_reviews:
        if dish_id not in unique_dishes or user_review > unique_dishes[dish_id][2]:
            unique_dishes[dish_id] = (user_id, 0, user_review)

    dish_matches = []
    for dish_id, (bud_id, comparison_num, bud_review) in unique_dishes.items():
        dish_matches.append((dish_id, bud_id, comparison_num, bud_review))

    # Filter Allergens and Dietary
    safe_matches = []
    for dish_id, bud_id, comparison_num, bud_review in dish_matches:
        dish_allergy = db.session.query(dish_allergen.allergen).filter(dish_allergen.dish_id == dish_id).all()
        dish_dietary = db.session.query(dish_restriction.restriction).filter(dish_restriction.dish_id == dish_id).all()
        dish_allergy_list = {a[0].lower() for a in dish_allergy}
        dish_dietary_list = {r[0].lower() for r in dish_dietary}

        # Vegan dishes are Vegetarian, Vegetarian are kosher and halal
        if "vegan" in dish_dietary_list:
            dish_dietary_list.add("vegetarian")
        if "vegetarian" in dish_dietary_list:
            dish_dietary_list.add("kosher") 
            dish_dietary_list.add("halal")
        
        if not (dish_allergy_list & user_allergy_list):
            if not user_dietary_list or user_dietary_list <= dish_dietary_list:
                safe_matches.append((dish_id, bud_id, comparison_num, bud_review))

    # Ranking: Average review + taste bud score + taste bud review + cuisine match  (weighted?)
    scored_matches = []
    for dish_id, bud_id, comparison_num, bud_review in safe_matches:

        avg_rating = (
            db.session.query(func.avg(review.rating))
            .filter(review.dish_id == dish_id)
            .scalar()
        ) or 3
        
        dish_cuisine = (
            db.session.query(dishTasteProfile.cuisine)
            .join(dish, dish.dish_id == dishTasteProfile.dish_id)
            .filter(dishTasteProfile.dish_id == dish_id)
            .scalar()
        ) or None

        # Normalize scores (0 to 1)
        bud_score = 1 - (comparison_num / 24)  # Adjust this if we change how tastebuddy score is determined
        review_score = bud_review / 5   
        avg_review = avg_rating / 5
        cuisine_score = user_cuisine_list.get(dish_cuisine, 0) / 5 # Will be a 5 if it is in there, 0 if it is not, result 1 or 0

        # Apply weights and turn to percent
        dish_score = round((
            (bud_score     * 0.55) +
            (review_score  * 0.25) +
            (avg_review    * 0.15) +
            (cuisine_score * 0.05)
        ) * 100, 1)

        scored_matches.append((dish_id, bud_id, dish_score))

    # Sort list based on score, descending and return
    scored_matches.sort(key=lambda x: x[2], reverse=True)
    return scored_matches

"""
Refactoring from restaurant routes.  Both restaurant and restaurant details require a collection of the restaurant
information and ratings based off the user.  Three methods come from this refactor:
get_restaurant_dish_scores - Returns a list of the dishes with scores for the user
get_restaurant_info - Returns a list of the information on the restaurant, including a rating for the user based on their dish scores
get_all_restaurant_info - calls get_restaurant_info on each restaurant id to get a full list of all the restaurants with their info
"""
def get_restaurant_dish_scores(user_id, restaurant_id):
    
    # Precondition check - user exists
    if not user_id:
        return []
    
    # Get dishes at the restaurant
    restaurant_dishes = {
        d[0] for d in db.session.query(dish.dish_id)
        .join(menuDishJunction, dish.dish_id == menuDishJunction.dish_id)
        .join(menu, menu.menu_id == menuDishJunction.menu_id)
        .filter(menu.restaurant_id == restaurant_id)
        .all()
    }

    # Get list of user dish percentages
    user_dish_matches = get_dish_recommendations(user_id)  # [0] = dish_id, [1] = buddy_id, [2] = % match

    # Filter list to combine the two
    matched_dishes = [d[0] for d in user_dish_matches if d[0] in restaurant_dishes]

    # Run some query to get data
    dish_data = {
        d.dish_id: d
        for d in db.session.query(dish).filter(dish.dish_id.in_(matched_dishes)).all()
    }

    dishes_with_match = [
        {
            "dish_id": d[0],
            "name": dish_data[d[0]].dish_name,
            "price": dish_data[d[0]].price,
            "image_url": dish_data[d[0]].image_path,
            "match_percentage": d[2],
            "available": dish_data[d[0]].available,
            "featured": dish_data[d[0]].featured,
        }
        for d in user_dish_matches if d[0] in dish_data
    ]

    return sorted(dishes_with_match, key=lambda x: x["match_percentage"], reverse=True)

def get_restaurant_info(user_id, restaurant_id):
    this_restaurant: restaurant = restaurant.query.get(restaurant_id)
    if not this_restaurant:
        return None
    
    restaurant_dishes = get_restaurant_dish_scores(user_id, this_restaurant.restaurant_id)

    matched_scores = [d["match_percentage"] for d in restaurant_dishes]
    restaurant_match_percent = round(sum(matched_scores) / len(matched_scores), 1) if matched_scores else 0

    hours_string = "<br>".join(
        f"{entry.days_of_week}: {entry.open_time.strftime('%I:%M %p')} - {entry.close_time.strftime('%I:%M %p')}"
        for entry in this_restaurant.operating_hours
    )

    recent_threshold = datetime.now() - timedelta(hours=4)

    recent_update = (
        db.session.query(liveUpdate)
        .filter(liveUpdate.restaurant_id == this_restaurant.restaurant_id)
        .filter(liveUpdate.created_at >= recent_threshold)
        .order_by(liveUpdate.created_at.desc())
        .first()
    )
    if recent_update:
        update_info = recent_update.update_content
    else:
        update_info = None

    return {
            "restaurant_id": this_restaurant.restaurant_id,
            "restaurant_name": this_restaurant.restaurant_name,
            "rating": this_restaurant.rating_average,
            "busy": this_restaurant.busy_average,
            "clean": this_restaurant.clean_average,
            "description": this_restaurant.description,
            "image_path": this_restaurant.image_path,
            "location": this_restaurant.location,
            "phone_number": this_restaurant.phone_number,
            "hours": hours_string, 
            "cuisine": this_restaurant.cuisine,
            "match_percentage": restaurant_match_percent,
            "dishes": restaurant_dishes,
            "live_update": update_info,

        }

def get_all_restaurant_info(user_id):
    all_restaurants = restaurant.query.all()
    return [get_restaurant_info(user_id, rest.restaurant_id) for rest in all_restaurants]

def get_follow_notifications(user_id):
    new_follows = (
        db.session.query(friends, user)
        .join(user, friends.user_id == user.user_id)
        .filter(friends.buddy_id == user_id, friends.seen == False)
        .all()
    )

    notifications = []
    for relation, follower in new_follows:
        is_following_back = db.session.query(friends).filter_by(
            user_id=user_id, buddy_id=follower.user_id
        ).first() is not None

        notifications.append({
            "follower_id": follower.user_id,
            "name": f"{follower.first_name} {follower.last_name}",
            "icon_path": follower.icon_path,
            "is_following_back": is_following_back,
        })

    return notifications


def relative_time(original_time):
    """
    Converts a datetime object into a relative time string for display
    based on the following rules:
    - Under 5 minutes: "just now"
    - Under 1 hour: "X minutes ago"
    - Under 1 day: "X hours ago"
    - Under 7 days: "yesterday" or "x days ago"
    - Under 30 Days: "last week" or "x weeks ago"
    - Over 30 days: "Month day, year"
    """
    now = datetime.now()
    diff = now - original_time
    seconds = diff.total_seconds()
    minutes = int(seconds // 60)
    hours = int(seconds // 3600)
    days = diff.days

    if seconds < 300:
        return "Just now"
    elif minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif days < 7:
        if days == 1:
            return "Yesterday"
        else:
            return f"{days} days ago"
    elif days < 30:
        weeks = int(days // 7)
        if weeks == 1:
            return "Last week"
        else:
            return f"{weeks} weeks ago"
    else:
        return original_time.strftime("%B %d, %Y")

"""
Normalize email is used to remove dot indifference and '+' extensions
from gmail accounts, as well as make emails lowercase for easier
case insensitive comparisons
:param email: email to be normalized
:return: normalized email address
"""
def normalize_email(email):
    email = email.lower().strip()
    name, domain = email.split("@")

    if "gmail" in domain or "google" in domain:
        name = name.split("+")[0]
        name = name.replace(".", "")

    return f"{name}@{domain}"

def get_average_dish_price(restaurant_id):
    """
    Get the average dish price for a restaurant
    :param restaurant_id: ID of restaurant to get average price for
    """
    averagePrice = (
        db.session.query(func.avg(dish.price))
        .join(menuDishJunction, dish.dish_id == menuDishJunction.dish_id)
        .join(menu, menu.menu_id == menuDishJunction.menu_id)
        .filter(menu.restaurant_id == restaurant_id)
        .scalar()
    )

    return round(averagePrice, 2)