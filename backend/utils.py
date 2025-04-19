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
from datetime import datetime, timedelta

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
    user_id - user ID
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
                "user_id": rev.user.user_id,
                "content": rev.content,
                "rating": rev.rating,
                "time_stamp": relative_time(rev.created_at),
            }
            for rev in reviews
        ]

    dish_score = None
    user_id = session.get("user_id")
    if user_id:
        recommendations = get_dish_recommendations(user_id)
        score_lookup = {d[0]: d[2] for d in recommendations}
        dish_score = score_lookup.get(dish_id, 42)

    return {
        "dish_id": dish_info.dish_id,
        "dish_name": dish_info.dish_name,
        "image": dish_info.image_path,
        "match_score": dish_score,
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
            dish_dietary_list.add("dairyfree")
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

def get_friend_reviews(user_id, limit=None):
    """
    gets the most recent review from each friend.
    returns all recent unique reviews, one per friend.
    
    :param user_id: current user ID
    :param limit: maximum number of friend reviews to return
    """
    # get all buddy IDs
    friend_ids = [
        f[0] for f in db.session.query(friends.buddy_id)
        .filter(friends.user_id == user_id)
        .all()
    ]

    if not friend_ids:
        return []

    # get all reviews from friends ordered by most recent first
    raw_reviews = (
        db.session.query(review)
        .filter(review.user_id.in_(friend_ids))
        .order_by(review.created_at.desc())
        .all()
    )

    # keep only 1 review per friend (most recent one)
    seen = set()
    unique_reviews = []
    for r in raw_reviews:
        if r.user_id not in seen:
            seen.add(r.user_id)
            unique_reviews.append(r)
        if limit and len(unique_reviews) >= limit:
            break

    # convert to list of dictionaries for the feed
    return [
        {
            "friend_id": r.user_id,
            "friend_name": f"{r.user.first_name} {r.user.last_name}",
            "friend_icon": r.user.icon_path,
            "content": r.content,
            "rating": r.rating,
            "dish_id": r.dish_id,
            "dish_name": r.dish.dish_name,
            "restaurant_id": r.dish.menu_dishes[0].menu.restaurant.restaurant_id,
            "restaurant_name": r.dish.menu_dishes[0].menu.restaurant.restaurant_name,
            "time_stamp": relative_time(r.created_at),
        }
        for r in unique_reviews
    ]

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

def get_saved_dishes(user_id, limit=None):
    """
    compiles a list of the user's saved dishes with oldest first
    returns dictionaries containing:
        - dish_name: name of dish they reviewed
        - dish_id: dish id to link to dish page
        - image: path to dish image
        - restaurant_name: name of restaurant where dish is
        - restaurant_id: to link to restaurant page
        - date_saved: date user saved the dish
    """
    user_info = db.session.query(user).get(user_id)

    if not user_info:
        return []

    saved_dishes = []
    for saved in sorted(user_info.saved_dishes, key=lambda x: x.date_saved):
        user_dish = saved.dish

        saved_dishes.append({
            "dish_id": user_dish.dish_id,
            "dish_name": user_dish.dish_name,
            "image": user_dish.image_path,
            "restaurant_name": user_dish.menu_dishes[0].menu.restaurant.restaurant_name,
            "restaurant_id": user_dish.menu_dishes[0].menu.restaurant.restaurant_id,
            "date_saved": saved.date_saved.strftime("%B %d, %Y"),
        })

    if limit:
        return saved_dishes[:limit]

    return saved_dishes

def get_live_updates(user_id, threshold=75, limit=None):
    """
    gets a list of the most recent updates for restaurants that match a threshold for the user

    :param user_id: id of user to base threshold for
    :param threshold: only restaurants above this % match will be returned
    :param limit: max number of updates to return
    :return: sorted list of restaurant dictionaries and their updates
    """

    all_restaurants = get_all_restaurant_info(user_id)
    match_rest_ids = [
        rest['restaurant_id'] for rest in all_restaurants
        if rest.get('match_percentage', 0) >= threshold
    ]

    if not match_rest_ids:
        return []
    
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)

    match_updates = (
        db.session.query(liveUpdate)
        .filter(liveUpdate.restaurant_id.in_(match_rest_ids))
        .filter(liveUpdate.user_id != user_id)
        .filter(liveUpdate.created_at >= twenty_four_hours_ago)
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

    if limit:
        return live_updates[:limit]

    return live_updates

def get_follow_notifications(user_id, limit=None):
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

    if limit:
        return notifications[:limit]

    return notifications

def get_daily_feed(user_id, offset=0, limit=100):
    """
    This function recreates the entire list everytime it is called which is BAD.
    then the offset is used to get the next set of items to show the user.
    ideally the list would be created once then the ones shown to the user
    would be popped off like a stack or queue in C++
    Sadly, I am time constrained and it isn't that important to the innovativeness of the project
    Get the daily feed for a user, combining friend reviews, recommended dishes,
    saved dishes, live updates, and follow notifications.
    :param user_id: ID of the user
    :param offset: Offset for pagination
    :param limit: Limit for pagination
    :return: List of feed items
    """

    # CHANGE THE LIMIT VALUES TO MESS WITH THE FEED SIZE AND FEEL 
    # Can also change review limit in get_friend_reviews
    friend_reviews = get_friend_reviews(user_id, limit=30)
    recommended_dishes = get_daily_dishes(user_id, limit=30)
    saved_dishes = get_saved_dishes(user_id, limit=30)
    live_updates = get_live_updates(user_id, limit=30)
    follow_notifications = get_follow_notifications(user_id, limit=30)

    combined_feed = []

    # consistent interleaving
    max_items = max(len(friend_reviews), len(recommended_dishes), len(saved_dishes), len(live_updates), len(follow_notifications))
    for i in range(max_items):
        if i < len(live_updates):
            combined_feed.append({"type": "update", "data": live_updates[i]})
        if i < len(recommended_dishes):
            combined_feed.append({"type": "dish", "data": recommended_dishes[i]})
        if i < len(friend_reviews):
            combined_feed.append({"type": "review", "data": friend_reviews[i]})
        if i < len(saved_dishes):
            combined_feed.append({"type": "saved", "data": saved_dishes[i]})
        if i < len(follow_notifications):
            combined_feed.append({"type": "follow", "data": follow_notifications[i]})

    result = combined_feed[offset:offset + limit]

    # import json
    # import os
    # # save to debug log
    # debug_info = {
    #     "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    #     "offset": offset,
    #     "limit": limit,
    #     "returned": len(result),
    #     "total": len(combined_feed),
    #     "items": result
    # }
    # os.makedirs("debug_logs", exist_ok=True)
    # with open("debug_logs/feed_debug.json", "a") as f:
    #     f.write(json.dumps(debug_info, indent=2))
    #     f.write("\n\n" + ("=" * 80) + "\n\n")

    return result

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
    roundPrice = round(averagePrice,2)
    roundedPrice = f"{roundPrice:.2f}"
    
    return roundedPrice