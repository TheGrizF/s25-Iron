from flask import Blueprint, render_template, session, request, flash, redirect, url_for, jsonify
from database import db
from database.models.dish import dish, menuDishJunction, menu 
from database.models.restaurant import restaurant
from database.models.user import friends, tasteComparisons, user
from backend.utils import get_average_dish_prices, get_bulk_restaurant_info, get_featured_dishes, get_group_dish_recommendations, get_dish_recommendations, get_daily_feed, get_all_restaurant_info, get_restaurant_info, get_average_dish_price
import json

daily_dish_bp = Blueprint('daily_dish', __name__)

@daily_dish_bp.route('/dailyDish')
def daily_dish():

    """
    This function renders the Daily Dish page for a logged-in user.

    This route checks if a user is logged in. If not, it redirects to the login page with a flash message.
    If authenticated, it retrieves a list of featured dishes and the user's personalized daily dish feed,
    then renders the dailyDish.html template with this information.

    Returns:
        Response: Rendered HTML page displaying the daily dish feed and featured dishes.
    """
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in first!", "error")
        return redirect(url_for("auth.login"))

    featured_dishes = get_featured_dishes()
    daily_dish_items = get_daily_feed(user_id, offset=0, limit=10)

    return render_template('dailyDish.html', featured_dishes=featured_dishes, feed_items=daily_dish_items[:10])


@daily_dish_bp.route('/search')
def search():

    """
    Displays the search page to the user.
    This route is responsible for displaying the search page to the user. 
    It returns the rendered HTML page for the search functionality, shown to the user.

    """
    return render_template('search.html')

@daily_dish_bp.route('/TasteBuds.html')
def TasteBuds():
     user_id = session.get('user_id')
     if not user_id:
        flash('Log in to view TasteBuddies.', 'error')
        return redirect(url_for('auth.index'))
    
     selected_user = user.query.get(user_id)

     # Fetch information on friends
     friendsList = db.session.query(user).join(friends, friends.buddy_id == user.user_id).filter(friends.user_id == user_id).all()
     matches = get_matches()

     return render_template('TasteBuds.html', friendslist=friendsList, matches=matches)

@daily_dish_bp.route('/createGroup', methods = ['POST','GET'])
def createGroup():

    """
    This function handles the creation of a dining group by storing selected buddies from a JSON request in the session.
    This function allows users to form a temporary group of dining partners for generating personalized restaurant matches.
    It plays a key role in enabling group-based recommendation features within the application.
    on a successful POST, there will be a JSON response with a success status.
    on error or GET it redirects to the overlappingRestaurants route.

    """
    user_id = session.get('user_id')
    try:
     groupData = request.get_json('userId')
     session['selectedBuddies'] = groupData.get('selectedBuddies',[])
     return jsonify({'status': 'success'})
    except Exception as e: 
         print("Error:",str(e))
   
    return redirect (url_for('daily_dish.overlappingRestaurants'))



@daily_dish_bp.route('/createGroup', methods = ['POST','GET'])
def overlappingDishes():
    user_id = session.get('user_id')
    selectedFriends = session.get('selectedBuddies',[])
    groupIDs = [item['userId'] for item in selectedFriends]
    activeGroup = groupIDs + [user_id]
    #Fetch information on members recommendations
    recommendations = []
    for member in activeGroupInfo:
     recommendationsList = get_dish_recommendations(member.user_id)
     recommendations.extend(recommendationsList)
    
    print(recommendations) #debug for all members recommendations

    seenDishes = {} #keep track of dishes seen and their match percentages
    matchingDishes = set() #keep track of matched dishes
   
    #iterate through list of recommendations checking to see if dish IDs match and if match percentages are over threshold
    for recommendation in recommendations:
         dish_id, matchPercentage = recommendation[0], recommendation[2]
         if matchPercentage > 75:
            if dish_id in seenDishes:
                seenDishes[dish_id].append(matchPercentage)
                if len(seenDishes[dish_id]) == len(activeGroup):
                    matchingDishes.add(dish_id)
            else:
                seenDishes[dish_id] = [matchPercentage]
   
    # for overlap iterate through matchingDishes set and make a list of the matches that meet requirements
    overlapping_recommendations = [rec for rec in recommendations if rec[0] in matchingDishes]
    print('overlap:',overlapping_recommendations) #debug for overlaps
    
    return redirect(url_for('daily_dish.groupMatch', index=0))

@daily_dish_bp.route('/overlappingRestaurants', methods = ['POST','GET'])
def overlappingRestaurants():
  
    user_id = session.get('user_id')
    selectedFriends = session.get('selectedBuddies',[])
    groupIDs = [item['userId'] for item in selectedFriends]
    
    # Clear previous group data
    clearSessionInfo = [
        'selectedBuddies', 'restaurant_list', 'highMatchingRestaurants',
        'mediumMatchingRestaurants', 'lowMatchingRestaurants', 'activeGroup',
        'activeGroupInfo', 'weightedScores'
        ]
    for key in clearSessionInfo:
        if key in session:
            session.pop(key)
   
    activeGroup = groupIDs + [user_id]
    activeGroupInfo = user.query.filter(user.user_id.in_(activeGroup)).all()

    restaurantRecommendations = []
    for member in activeGroupInfo:
        recommendationsList = get_all_restaurant_info(member.user_id)
        restaurantRecommendations.extend([
         (rec.get('restaurant_id'),rec.get('restaurant_name'),rec.get('match_percentage')) 
        for rec in recommendationsList ])
    print(restaurantRecommendations) 

    # Track seen restaurants and weighted scores
    seenRestaurants = {}
    weightedScores = {}

   # Get each users match percentages per restaurant (stored in seenRestaurants)
    for recommendations in restaurantRecommendations:
        restaurant_id, restaurant_name, matchPercentage = recommendations
        if restaurant_id not in seenRestaurants:
            seenRestaurants[restaurant_id] = []
        seenRestaurants[restaurant_id].append(matchPercentage)
    
    # Calculate weighted match percentages (iterating through items in seenRestaurants)
    for restaurant_id, percentages in seenRestaurants.items():
        # Apply weights to extreme values
        weightedMatchPercentage = sum(
           matchPercentage * 1.2 if matchPercentage > 90 else matchPercentage * 0.8 if matchPercentage < 50 else matchPercentage
          for matchPercentage in percentages
        ) #lowest number seen 62.6 highest 88.4
        weightedAvg = weightedMatchPercentage / len(percentages)
        weightedScores[restaurant_id] = round(weightedAvg,2) 
    print('weightedScores:',weightedScores) #debug 


    # Categorize restaurants based on weighted scores (numbers may need adjustment)
    highMatchingRestaurants = {rid for rid, matchPercentage in weightedScores.items() if matchPercentage > 80}
    mediumMatchingRestaurants = {rid for rid, matchPercentage in weightedScores.items() if 65<= matchPercentage <= 80}
    lowMatchingRestaurants = {rid for rid, matchPercentage in weightedScores.items() if matchPercentage < 65}
   



    print (highMatchingRestaurants)
    session['highMatchingRestaurants'] = list(highMatchingRestaurants)
    session['mediumMatchingRestaurants'] = list(mediumMatchingRestaurants)
    session['lowMatchingRestaurants'] = list(lowMatchingRestaurants)  
    session['weightedScores'] = weightedScores
    session['activeGroup'] = activeGroupInfo

    return redirect(url_for('daily_dish.groupMatch', index=0))



@daily_dish_bp.route('/groupMatch')
@daily_dish_bp.route('/groupMatch/<int:index>')
def groupMatch(index=0):
    user_id = session.get('user_id')
    
    highMatchingRestaurants = session.get('highMatchingRestaurants',[])
    mediumMatchingRestaurants = session.get('mediumMatchingRestaurants',[])
    lowMatchingRestaurants = session.get('lowMatchingRestaurants',[])
    weightedScores = session.get('weightedScores', {})
    activeGroupInfo = session.get('activeGroup')
    print('weightedScores:',weightedScores)
    
    # Added this session so it wouldn't recalculate when pagination is used
    if 'restaurant_list' not in session or not session['restaurant_list']:
        restaurants = []

        # Sort restaurants in descending order to make this meaningful
        sorted_ids = sorted(weightedScores, key=lambda rid: weightedScores[rid], reverse=True)

        # Get the top restaurant IDs with scores above 70 or the top 5, whichever is greater
        top_restaurant_ids = [rid for rid in sorted_ids if weightedScores[rid] >= 70]
        if len(top_restaurant_ids) < 5:
            # Add more restaurants to reach at least 5 (if available)
            additional_ids = [rid for rid in sorted_ids if rid not in top_restaurant_ids][:5-len(top_restaurant_ids)]
            top_restaurant_ids.extend(additional_ids)

        # Assign top dishes per group member
        top_dishes_by_member = {}

        group_dish_recommendations = get_group_dish_recommendations([user.user_id for user in activeGroupInfo])

        for member in activeGroupInfo:
            user_dishes = {}
            dish_recommendations = group_dish_recommendations.get(member.user_id, [])
            
            # Find each member's top dish per restaurant
            for dish_id, tastebuddy_id, dish_score, rest_id in dish_recommendations:
                if rest_id in top_restaurant_ids:
                    if (rest_id not in user_dishes) or (dish_score > user_dishes[rest_id][2]):
                        user_dishes[rest_id] = (dish_id, tastebuddy_id, dish_score)
            
            top_dishes_by_member[member.user_id] = user_dishes
        
        avg_prices = get_average_dish_prices(top_restaurant_ids)
        rest_info_map = get_bulk_restaurant_info(user_id, top_restaurant_ids)

        all_dish_ids = {
            dish_id for member in activeGroupInfo
            for dish_id in [
                top_dishes_by_member.get(member.user_id, {}).get(rest_id, (None,))[0]
                for rest_id in top_dishes_by_member.get(member.user_id, {})
            ] if dish_id is not None
        }

        dishes = {
            d.dish_id: d for d in dish.query.filter(dish.dish_id.in_(all_dish_ids)).all()
        }
        
        for restaurant_id in top_restaurant_ids:
            restaurantInfo = rest_info_map.get(restaurant_id)
            if restaurantInfo:
                restaurantInfo['weightedScores'] = weightedScores[restaurant_id]
                restaurantInfo['average_price'] = avg_prices.get(restaurant_id, "42")
                restaurantInfo['restaurant_name'] = restaurantInfo.get('restaurant_name')
                if restaurant_id in highMatchingRestaurants:
                    restaurantInfo['confidence'] = 'High'
                elif restaurant_id in mediumMatchingRestaurants:
                    restaurantInfo['confidence'] = 'Medium'
                else:
                    restaurantInfo['confidence'] = 'Low'
                # Add member data to restaurant
                restaurantInfo['members'] = []
                
                # Get dish details for each member's top pick at this restaurant
                dish_details = {}
                for member in activeGroupInfo:
                    member_dishes = top_dishes_by_member.get(member.user_id, {})
                    if restaurant_id in member_dishes:
                        dish_id, tastebuddy_id, dish_score = member_dishes[restaurant_id]
                        
                        # Lazily fetch dish info as needed
                        if dish_id not in dish_details:
                            dish_obj = dishes.get(dish_id)
                            if dish_obj:
                                dish_details[dish_id] = {
                                    'dish_id': dish_id,
                                    'dish_name': dish_obj.dish_name,
                                    'price': dish_obj.price,
                                    'image_path': dish_obj.image_path
                                }
                        
                        if dish_id in dish_details:
                            restaurantInfo['members'].append({
                                'user_id': member.user_id,
                                'first_name': member.first_name,
                                'last_name': member.last_name,
                                'icon_path': member.icon_path,
                                'top_dish': dish_details[dish_id],
                                'match_score': dish_score
                            })
                

                restaurants.append(restaurantInfo)
       
        for r in restaurants:
            print (r['restaurant_id'],r['average_price'],r['confidence']) #debug 
        
        session['restaurant_list'] = restaurants

    else:
        restaurants =session['restaurant_list'] # For future navigational purposes

    activeGroup = [ 
        {
        "user_id": member.user_id,
        "first_name": member.first_name,
        "last_name": member.last_name,
        "icon_path": member.icon_path,
        } for member in activeGroupInfo
        ]
    print('Info:',activeGroup)
    return render_template('groupMatch.html',restaurants = restaurants,highMatchingRestaurants = highMatchingRestaurants,mediumMatchingRestaurants=mediumMatchingRestaurants,lowMatchingRestaurants= lowMatchingRestaurants,weightedScores=weightedScores, index=index, activeGroup=activeGroup)

@daily_dish_bp.route('/restaurant/<id>')
def restaurant_detail(id):

    """
    This function renders the restaurant detail page for a specific restaurant.
    This function is used when a user navigates to the restaurant detail view using a specific restaurant ID.

    Parameter:
        id: The unique identifier of the restaurant passed through the URL.

    Returns:
        The 'restaurant_detail.html' template for the specified restaurant.

    """
    return render_template('restaurant_detail.html')

@daily_dish_bp.route('/get-buddy/<int:user_id>')
def get_buddy(user_id):

    """
    Retrieves and returns profile information for a specific buddy (user).

    This function queries the database for a user based on the provided user ID.
    If the buddy is found, their user ID, icon path, first name, and last name are returned.
    If the buddy is not found or an error occurs, an appropriate error message is returned.

    Parameter:
        user_id: The unique identifier of the user whose buddy data is being requested.

    """
    try:
        buddy = user.query.filter_by(user_id=user_id).first()
        if buddy:
            return jsonify({
                'user_id': buddy.user_id,
                'icon_path': buddy.icon_path,
                'first_name': buddy.first_name,
                'last_name': buddy.last_name
            })
        else:
            return jsonify({'error': 'Buddy not found'}), 404
    except Exception as e:
        print(f"Error: {str(e)}")  # Debugging
        return jsonify({'error': 'Internal Server Error'}), 500 

def get_matches():#This doesn't work correctly
    try:
        user_id = session.get('user_id')
        if not user_id:
            flash('Log in to view TasteBuddies.', 'error')
            return redirect(url_for('auth.index'))

        matches = db.session.query(
        tasteComparisons.compare_to,
        user.first_name,
        user.last_name,
        tasteComparisons.comparison_num,
        user.icon_path
    ).join(user, user.user_id == tasteComparisons.compare_to).filter(
        tasteComparisons.compare_from == user_id
    ).order_by(tasteComparisons.comparison_num).all()

        results = [{ "user_id": match.compare_to,
                "first_name": match.first_name,
                "last_name": match.last_name,
                "match_score": round((48 - match.comparison_num) / 48 * 100, 1),
                "icon_path": match.icon_path} 
                for match in matches if round((48 - match.comparison_num) / 48 * 100, 1) > 80]

        return results

    except Exception as e:
        print(f"Error in get_matches: {e}")
        return []
    
@daily_dish_bp.route('/mark-follow-seen/<int:follow_id>', methods=['POST'])
def mark_follow_seen(follow_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    follow_entry = friends.query.filter_by(user_id=follow_id, buddy_id=user_id, seen=False).first()

    if follow_entry:
        follow_entry.seen = True
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Follow not found or already seen'})

@daily_dish_bp.route('/follow-back/<int:follower_id>', methods=['POST'])
def follow_back(follower_id):
    current_user_id = session.get('user_id')
    if not current_user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    already_following = db.session.query(friends).filter_by(
        user_id=current_user_id, buddy_id=follower_id
    ).first()

    if not already_following:
        new_follow = friends(user_id=current_user_id, buddy_id=follower_id)
        db.session.add(new_follow)
        db.session.commit()

    return jsonify({"success": True})

@daily_dish_bp.route('/load-more-feed')
def load_more_feed():
    user_id = session.get('user_id')
    offset = int(request.args.get('offset', 0))
    new_feed_items = get_daily_feed(user_id, offset=offset, limit=10)
    print(f"Offset: {offset}")
    
    rendered_html = ""
    for item in new_feed_items:
        if item["type"] == "dish":
            rendered_html += render_template("components/feed_card.html", item=item)
        elif item["type"] == "review":
            rendered_html += render_template("components/feed_card.html", item=item)
        elif item["type"] == "saved":
            rendered_html += render_template("components/feed_card.html", item=item)
        elif item["type"] == "update":
            rendered_html += render_template("components/feed_card.html", item=item)
        elif item["type"] == "follow":
            rendered_html += render_template("components/feed_card.html", item=item)

    # import os
    # from datetime import datetime
    # # save rendered_html to a separate debug file
    # os.makedirs("debug_logs", exist_ok=True)
    # timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # with open(f"debug_logs/rendered_html_{timestamp}.html", "w", encoding="utf-8") as f:
    #     f.write(rendered_html)


    return jsonify({
        "feed_html": rendered_html,
        "count": len(new_feed_items),
        "has_more": len(new_feed_items) == 10
    })

@daily_dish_bp.route('/groupMatch/navigate/<int:index>')
def navigate_restaurant(index=0):
    restaurants = session.get('restaurant_list', [])
    
    # Ensure index is within bounds
    if not restaurants:
        index = 0
    elif index < 0:
        index = len(restaurants) - 1  # Loop to the end
    elif index >= len(restaurants):
        index = 0  # Loop back to beginning
        
    return render_template('groupMatch.html',
                          restaurants=restaurants,
                          index=index,
                          highMatchingRestaurants=session.get('highMatchingRestaurants',[]),
                          mediumMatchingRestaurants=session.get('mediumMatchingRestaurants',[]),
                          lowMatchingRestaurants=session.get('lowMatchingRestaurants',[]),
                          weightedScores=session.get('weightedScores'))

