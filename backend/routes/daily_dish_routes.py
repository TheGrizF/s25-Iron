from flask import Blueprint, render_template, session, request, flash, redirect, url_for, jsonify
from database import db
from database.models.dish import dish
from database.models.user import friends, tasteComparisons, user
from backend.utils import get_featured_dishes, get_daily_dishes, get_friend_reviews, get_saved_dishes, get_dish_recommendations, get_live_updates, get_all_restaurant_info, get_restaurant_info
import json
daily_dish_bp = Blueprint('daily_dish', __name__)

@daily_dish_bp.route('/dailyDish')
def daily_dish():
    user_id = session.get('user_id')
    if not user_id:
        return "Not Logged In", 404
    

    featured_dishes = get_featured_dishes()

    friend_reviews = get_friend_reviews(user_id, 10)
    recommended_dishes = get_daily_dishes(user_id, 10)
    saved_dishes = get_saved_dishes(user_id)
    live_updates = get_live_updates(user_id)

    daily_dish_items = []
    for i in range(max(len(friend_reviews), len(recommended_dishes), len(saved_dishes))):
        if i < len(live_updates):
            daily_dish_items.append({"type": "update", "data": live_updates[i]})
        if i < len(recommended_dishes):
            daily_dish_items.append({"type": "dish", "data": recommended_dishes[i]})
        if i < len(friend_reviews):
            daily_dish_items.append({"type": "review", "data": friend_reviews[i]})
        if i < len(saved_dishes):
            daily_dish_items.append({"type": "saved", "data": saved_dishes[i]})

    return render_template('dailyDish.html', featured_dishes=featured_dishes, feed_items=daily_dish_items)


@daily_dish_bp.route('/search')
def search():
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
    
    return redirect(url_for('daily_dish.groupMatch'))

@daily_dish_bp.route('/overlappingRestaurants', methods = ['POST','GET'])
def overlappingRestaurants():
  
    user_id = session.get('user_id')
    selectedFriends = session.get('selectedBuddies',[])
    groupIDs = [item['userId'] for item in selectedFriends]
    activeGroup = groupIDs + [user_id]
    activeGroupInfo = user.query.filter(user.user_id.in_(activeGroup)).all()

    restaurantRecommendations = []
    for member in activeGroupInfo:
        recommendationsList = get_all_restaurant_info(member.user_id)
        restaurantRecommendations.extend([
         (rec.get('restaurant_id'),rec.get('restaurant_name'),rec.get('match_percentage')) 
        for rec in recommendationsList ])
    print(restaurantRecommendations) 

    highSeenRestaurants = {}
    mediumSeenRestaurants = {}
    lowSeenRestaurants = {}
    highMatchingRestaurants = set()
    mediumMatchingRestaurant = set()
    lowMatchingRestaurant = set()
    
    for recommendations in restaurantRecommendations:
        restaurant_id, matchPercentage = recommendations[0], recommendations[2]
        if matchPercentage > 75:
            if restaurant_id in highSeenRestaurants:
                highSeenRestaurants[restaurant_id].append(matchPercentage)
                if len(highSeenRestaurants[restaurant_id]) == len(activeGroup):
                    highMatchingRestaurants.add(restaurant_id)
            else:
                highSeenRestaurants[restaurant_id] = [matchPercentage]
        if matchPercentage > 50 and matchPercentage < 75:
            if restaurant_id in mediumSeenRestaurants:
                mediumSeenRestaurants[restaurant_id].append(matchPercentage)
                if len(mediumSeenRestaurants[restaurant_id]) == len(activeGroup):
                    mediumMatchingRestaurant.add(restaurant_id)
            else:
                mediumSeenRestaurants[restaurant_id] = [matchPercentage]
        if matchPercentage < 50:
            if restaurant_id in lowSeenRestaurants:
                lowSeenRestaurants[restaurant_id].append(matchPercentage)
                if len(lowSeenRestaurants[restaurant_id]) == len(activeGroup):
                    lowMatchingRestaurant.add(restaurant_id)
            else:
                lowSeenRestaurants[restaurant_id] = [matchPercentage]
            
    highOverlappingRecommendations =[rec for rec in restaurantRecommendations if rec[0] in highMatchingRestaurants]
    mediumOverlappingRecommendations =[rec for rec in restaurantRecommendations if rec[0] in mediumMatchingRestaurant]
    lowOverlappingRecommendations =[rec for rec in restaurantRecommendations if rec[0] in lowMatchingRestaurant]
    print('High overlap:',highOverlappingRecommendations)
    print('Medium overlap:',mediumOverlappingRecommendations)
    print('Low overlap:',lowOverlappingRecommendations)
    session['highOverlappingRecommendations'] = highOverlappingRecommendations
    session['mediumOverlappingRecommendations'] = mediumOverlappingRecommendations  
    session['lowOverlappingRecommendations'] = lowOverlappingRecommendations

    return redirect(url_for('daily_dish.groupMatch'))



@daily_dish_bp.route('/groupMatch')
def groupMatch():
    user_id = session.get('user_id')
    highOverlappingRecommendations = session.get('highOverlappingRecommendations',[])
    mediumOverlappingRecommendations = session.get('mediumOverlappingRecommendations',[])   
    lowOverlappingRecommendations = session.get('lowOverlappingRecommendations',[])
   
    highRecommendedRestaurants = []
    for recommendation in highOverlappingRecommendations:
        if recommendation[0] not in highRecommendedRestaurants:
         highRecommendedRestaurants.append(recommendation[0])
    print('highRecommendedRestaurants:',highRecommendedRestaurants) 
    mediumRecommendedRestaurants = []
    for recommendation in mediumOverlappingRecommendations:
        if recommendation[0] not in mediumRecommendedRestaurants:
         mediumRecommendedRestaurants.append(recommendation[0])
    print('mediumRecommendation:',mediumRecommendedRestaurants)
    lowRecommendedRestaurants = []
    for recommendation in lowOverlappingRecommendations:   
        if recommendation[0] not in lowRecommendedRestaurants:
         lowRecommendedRestaurants.append(recommendation[0])
    print('lowRecommendation:',lowRecommendedRestaurants)

    restaraunts =  []
    for restaurant_id in highRecommendedRestaurants:
        restaurant_info = get_restaurant_info(user_id,restaurant_id)
        if restaurant_info:
            restaraunts.append(restaurant_info)
    
     
    for restaurant_id in mediumRecommendedRestaurants:
        restaurant_info = get_restaurant_info(user_id,restaurant_id)
        if restaurant_info:
            restaraunts.append(restaurant_info)
    
  
    for restaurant_id in lowRecommendedRestaurants:
        restaurant_info = get_restaurant_info(user_id,restaurant_id)
        if restaurant_info:
            restaraunts.append(restaurant_info)
    
    return render_template('groupMatch.html',restaurants= restaraunts,highRecommendedRestaurants=highRecommendedRestaurants, mediumRecommendedRestaurants=mediumRecommendedRestaurants, lowRecommendedRestaurants=lowRecommendedRestaurants)

@daily_dish_bp.route('/restaurant/<id>')
def restaurant_detail(id):
    return render_template('restaurant_detail.html')

@daily_dish_bp.route('/get-buddy/<int:user_id>')
def get_buddy(user_id):
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
                "match_score": round((24 - match.comparison_num) / 24 * 100, 1),
                "icon_path": match.icon_path} 
                for match in matches if round((24 - match.comparison_num) / 24 * 100, 1) > 75]

        return results

    except Exception as e:
        print(f"Error in get_matches: {e}")
        return []
    