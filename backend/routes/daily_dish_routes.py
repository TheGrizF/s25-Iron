from flask import Blueprint, render_template, session, request, flash, redirect, url_for, jsonify
from database import db
from database.models.dish import dish
from database.models.user import friends, tasteComparisons, user
from backend.utils import get_featured_dishes, get_daily_dishes, get_friend_reviews, get_saved_dishes, get_dish_recommendations, get_live_updates
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
    groupData = request.get_json()
    selectedFriends = groupData.get('selectedBuddies',[])
    
    #debug to see if user_ids coming through
    print('Received selected buddies:', selectedFriends)
    
    # Add list containning current user to list of selected
    activeGroup = [user_id] + selectedFriends
    
    #Fetch information on users in active group
    activeGroupInfo = user.query.filter(user.user_id.in_(activeGroup)).all()
    
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
    
    return redirect(url_for('daily_dish.groupMatch', activeGroup = activeGroupInfo, recommendations = recommendations))

@daily_dish_bp.route('/groupMatch')
def groupMatch():
   return render_template('groupMatch.html')

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
    