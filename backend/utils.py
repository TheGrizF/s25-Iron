"""
Use this to create all the helper functions for the routes.
Keeps them organized so we can use them again if we need to.
"""
from datetime import datetime, timedelta
from flask import session
from sqlalchemy import func
from sqlalchemy.orm import joinedload
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

def get_all_dish_info(dish_recommendations, saved_dish_ids):
    dish_ids = [d[0] for d in dish_recommendations]
    score_lookup = {d[0]: d[2] for d in dish_recommendations}

    dishes = db.session.query(dish).filter(dish.dish_id.in_(dish_ids)).all()
    dishes_by_id = {d.dish_id: d for d in dishes}

    avg_ratings = dict(
        db.session.query(review.dish_id, func.avg(review.rating))
        .filter(review.dish_id.in_(dish_ids))
        .group_by(review.dish_id)
        .all()
    )

    result = []
    for dish_id in dish_ids:
        d = dishes_by_id.get(dish_id)
        if not d or not d.menu_dishes:
            continue

        restaurant = d.menu_dishes[0].menu.restaurant

        result.append({
            "dish_id": d.dish_id,
            "dish_name": d.dish_name,
            "image": d.image_path,
            "match_score": score_lookup.get(d.dish_id, 0),
            "average_rating": round(avg_ratings.get(d.dish_id, 0), 1),
            "restaurant_id": restaurant.restaurant_id,
            "restaurant_name": restaurant.restaurant_name,
            "description": d.description,
            "price": d.price,
            "available": d.available,
            "is_saved": d.dish_id in saved_dish_ids,
        })

    return result


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
    # user_tp = db.session.query(user).filter(user.user_id == user_id).first()
    user_allergy = db.session.query(user_allergen.allergen).filter(user_allergen.user_id == user_id).all()
    user_dietary = db.session.query(user_restriction.restriction).filter(user_restriction.user_id == user_id).all()
    user_cuisine = db.session.query(cuisineUserJunction).filter(cuisineUserJunction.user_id == user_id).all()

    # make lists (if aplicable)
    user_allergy_list = {a[0].lower() for a in user_allergy}
    user_dietary_list = {r[0].lower() for r in user_dietary}
    user_cuisine_list = {c.cuisine_id: c.preference_level for c in user_cuisine}

    # get users own reviews
    user_reviews_raw = (
        db.session.query(review.dish_id, review.rating)
        .filter(review.user_id == user_id)
        .all()
    )
    user_reviews = {dish_id: rating for dish_id, rating in user_reviews_raw}

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

    unique_dishes = {}

    # Add user reviewed dishes to list
    for dish_id, rating in user_reviews.items():
        unique_dishes[dish_id] = (user_id, 0, rating)

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

        restaurant_id = (
            db.session.query(menu.restaurant_id)
            .join(menuDishJunction, menu.menu_id == menuDishJunction.menu_id)
            .filter(menuDishJunction.dish_id == dish_id)
            .scalar()
        )

        # Normalize scores (0 to 1)
        bud_score = 1 - (comparison_num / 48)  # Adjust this if we change how tastebuddy score is determined
        if bud_score >= 0.90:
            review_weight = 1.0
        elif bud_score >= 0.80:
            review_weight = 0.75
        elif bud_score >= 0.70:
            review_weight = 0.50
        elif bud_score >= 0.60:
            review_weight = 0.25
        else:
            review_weight = 0.0
        review_score = (bud_review / 5) * review_weight
        avg_review = avg_rating / 5
        cuisine_score = user_cuisine_list.get(dish_cuisine, 0) / 5 # Will be a 5 if it is in there, 0 if it is not, result 1 or 0



        # Weight based on own review
        own_review = user_reviews.get(dish_id)

        if own_review is not None:
        # Apply weights
            base_score = (
                ((own_review / 5) * 0.85) +
                (avg_review    * 0.10) +
                (cuisine_score * 0.05)
            )
        else:
            if bud_score < 0.9:
                penalty = (1 - (0.9 - bud_score)) ** 2
                bud_score *= penalty
            base_score = (
                (bud_score     * 0.65) +
                (review_score  * 0.20) +
                (avg_review    * 0.10) +
                (cuisine_score * 0.05)
            )

        adjusted_score = max(0, min(1, base_score))
        dish_score = round(adjusted_score * 100, 1)
            
        scored_matches.append((dish_id, bud_id, dish_score, restaurant_id))

    # Sort list based on score, descending and return
    scored_matches.sort(key=lambda x: x[2], reverse=True)
    return scored_matches

def get_group_dish_recommendations(user_ids):
    """"
    Method to get a dictionary of dish recommendations for multiple users.
    :param user_ids: list of user ids to get group recommendations for
    :return group_recommendations: formatted dictionary { user_id: [(dish_id, tastebuddy_id, score), ...]}
    """
    group_recommendations = {}
    for userid in user_ids:
        try:
            group_recommendations[userid] = get_dish_recommendations(userid)
        except Exception as e:
            print(f"Failed to get recomendations for user {userid}: {e}")
            group_recommendations[userid] = []
    return group_recommendations

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

def get_restaurant_info(user_id, this_restaurant, update_info=None):

    restaurant_dishes = get_restaurant_dish_scores(user_id, this_restaurant.restaurant_id)

    matched_scores = [d["match_percentage"] for d in restaurant_dishes]
    restaurant_match_percent = round(sum(matched_scores) / len(matched_scores), 1) if matched_scores else 0

    hours_string = "<br>".join(
        f"{entry.days_of_week}: {entry.open_time.strftime('%I:%M %p')} - {entry.close_time.strftime('%I:%M %p')}"
        for entry in this_restaurant.operating_hours
    )

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
    recent_update_threshold = datetime.now() - timedelta(hours=4)

    all_restaurants = (
        db.session.query(restaurant)
        .options(
            joinedload(restaurant.operating_hours),
            joinedload(restaurant.menu)
                .joinedload(menu.menu_dishes)
                .joinedload(menuDishJunction.dish)
        ).all()
    )

    recent_updates = (
        db.session.query(liveUpdate)
        .filter(liveUpdate.created_at >= recent_update_threshold)
        .order_by(liveUpdate.created_at.desc())
        .all()
    )
    update_map = {}
    for update in recent_updates:
        if update.restaurant_id not in update_map:
            update_map[update.restaurant_id] = update.update_content

    return [get_restaurant_info(user_id, rest, update_map.get(rest.restaurant_id)) for rest in all_restaurants]

def get_bulk_restaurant_info(user_id, restaurant_ids):
    """
    Batch call to getting restaurant info for multiple restaurants.
    :param user_id: user id for restaurant rating
    :param restaurant_ids: list of restaurant ids to get rating for
    :return: { restaurant_id: info_dict }
    """
    restaurants = db.session.query(restaurant).options(
        joinedload(restaurant.operating_hours),
        joinedload(restaurant.menu)
            .joinedload(menu.menu_dishes)
            .joinedload(menuDishJunction.dish)
    ).filter(restaurant.restaurant_id.in_(restaurant_ids)).all()

    return {
        rest.restaurant_id: get_restaurant_info(user_id, rest)
        for rest in restaurants
    }

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
        .options(
            joinedload(review.user)
            .load_only(user.first_name,
                       user.last_name,
                       user.icon_path),
            joinedload(review.dish)
            .joinedload(dish.menu_dishes)
            .joinedload(menuDishJunction.menu)
            .joinedload(menu.restaurant)
        )
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
    
    new_dishes = [dish for dish in recommended if dish[1] != user_id and dish[2] >= 70][:limit]

    dish_ids = [dish[0] for dish in new_dishes]

    dishes = {
        d.dish_id: d for d in db.session.query(dish)
        .options(
            joinedload(dish.menu_dishes)
                .joinedload(menuDishJunction.menu)
                .joinedload(menu.restaurant),
            joinedload(dish.reviews).joinedload(review.user)
        )
        .filter(dish.dish_id.in_(dish_ids)).all()
    }

    match_scores = {
        m.compare_to: m.comparison_num
        for m in db.session.query(tasteComparisons)
        .filter(tasteComparisons.compare_from == user_id)
    }

    buddy_reviews = {}
    for d in dishes.values():
        for rev in sorted(d.reviews, key=lambda r: r.created_at, reverse=True):
            if (
                rev.user_id != user_id and 
                match_scores.get(rev.user_id, 0) <= 14 and
                rev.rating > 3
            ):
                buddy_reviews[d.dish_id] = {
                    "buddy_name": f"{rev.user.first_name} {rev.user.last_name}",
                    "buddy_icon": rev.user.icon_path,
                    "review_content": rev.content,
                    "time_stamp": relative_time(rev.created_at),
                    "buddy_rating": rev.rating,
                }
            break
    
    daily_dishes = [
        {
            "dish_id": id,
            "name": dishes[id].dish_name,
            "image_path": dishes[id].image_path,
            "restaurant": dishes[id].menu_dishes[0].menu.restaurant.restaurant_name,
            "restaurant_id": dishes[id].menu_dishes[0].menu.restaurant.restaurant_id,
            "match_score": score,
            **buddy_reviews.get(id, {})
        }
        for id, _, score, _ in new_dishes 
        if id in dishes and id in buddy_reviews
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
    user_info = db.session.query(user).options(
        joinedload(user.saved_dishes)
        .joinedload(savedDishes.dish)
        .joinedload(dish.menu_dishes)
        .joinedload(menuDishJunction.menu)
        .joinedload(menu.restaurant)
    ).get(user_id)

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
        .options(
            joinedload(liveUpdate.user),
            joinedload(liveUpdate.restaurant)
        )
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

    follow_back = {
        following.buddy_id for following in db.session.query(friends)
        .filter_by(user_id=user_id)
        .all()
    }

    notifications = []
    for relation, follower in new_follows:
        notifications.append({
            "follower_id": follower.user_id,
            "name": f"{follower.first_name} {follower.last_name}",
            "icon_path": follower.icon_path,
            "is_following_back": follower.user_id in follow_back,
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

def get_average_dish_prices(restaurant_ids):
    """
    Batch call to get all avg prices for restaurants.
    :param restaurant_ids: List of restaurant ids to get average prices
    :return: dictionary format { restaurant_id: "avg_price_str" }
    """
    results = (
        db.session.query(menu.restaurant_id, func.avg(dish.price))
        .join(menuDishJunction, dish.dish_id == menuDishJunction.dish_id)
        .join(menu, menu.menu_id == menuDishJunction.menu_id)
        .filter(menu.restaurant_id.in_(restaurant_ids))
        .group_by(menu.restaurant_id)
        .all()
    )
    return {rest_id: f"{round(avg, 2):.2f}" for rest_id, avg in results}

def get_filtered_sorted_dishes(user_id, search="", filter_by="all", sort_by="match_score"):
    dish_recommendations = get_dish_recommendations(user_id)
    dish_scores = {d[0]: d[2] for d in dish_recommendations}
    saved_dish_ids = {saved.dish_id for saved in savedDishes.query.filter_by(user_id=user_id).all()}

    all_dishes = get_all_dish_info(dish_recommendations, saved_dish_ids)

    # filter
    if filter_by != 'all':
        if filter_by == "four_stars":
            all_dishes = [d for d in all_dishes if 4.0 <= d["average_rating"] <= 5.0]
        elif filter_by == "three_stars":
            all_dishes = [d for d in all_dishes if 3.0 <= d["average_rating"] < 4.0]
        elif filter_by == "two_stars":
            all_dishes = [d for d in all_dishes if 2.0 <= d["average_rating"] < 3.0]
        elif filter_by == "one_star":
            all_dishes = [d for d in all_dishes if 1.0 <= d["average_rating"] < 2.0]
        elif filter_by == "saved":
            all_dishes = [d for d in all_dishes if d["dish_id"] in saved_dish_ids]

    # search
    exclude_words = {'the', 'a', 'and'}
    searched_keywords = [word for word in search.lower().split() if word not in exclude_words]
    if searched_keywords:
        all_dishes = [
            d for d in all_dishes if any(
                keyword in d['dish_name'].lower() or
                keyword in d['restaurant_name'].lower() or
                keyword in d['description'].lower()
                for keyword in searched_keywords
            )
        ]
    return sort_dishes(all_dishes, sort_by)

def sort_dishes(filtered_dishes, sort_by="match_score"):
    if sort_by == "match_score":
        return sorted(filtered_dishes, key=lambda d: d["match_score"], reverse=True)
    elif sort_by == "name":
        return sorted(filtered_dishes, key=lambda d: d["dish_name"].lower())
    elif sort_by == "price":
        return sorted(filtered_dishes, key=lambda d: float(d["price"]))
    elif sort_by == "restaurant_name":
        return sorted(filtered_dishes, key=lambda d: d["restaurant_name"])
    else:
        return filtered_dishes