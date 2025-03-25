from flask import Blueprint, render_template, session, request, flash, redirect, url_for, jsonify
from database import db
from database.models.dish import dish
from database.models.user import friends, user
from backend.utils import get_featured_dishes, get_daily_dishes, get_friend_reviews, get_saved_dishes, get_dish_recommendations
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

    daily_dish_items = []
    for i in range(max(len(friend_reviews), len(recommended_dishes), len(saved_dishes))):
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

     return render_template('TasteBuds.html', friendslist=friendsList)

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

@daily_dish_bp.route('/review', methods=['GET', 'POST'])
def review():
    user = {'firstName': 'Person-I-Know'} #Umm, don't know how to connect it with db right now 
    return render_template('review.html', user = user)

@daily_dish_bp.route('/TasteBuds')
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
            tasteComparisons.comparison_num
        ).join(user, user.user_id == tasteComparisons.compare_to).filter(
            tasteComparisons.compare_from == user_id,
            tasteComparisons.comparison_num <= 6
        ).order_by(tasteComparisons.comparison_num).all()




        results =[{
            "user_id": match.user_id,
            "name": f"{match.first_name} {match.last_name}",
            "match_score": round(( 24 - match.comparison_num) / 24 * 100, 1)
        } for match in matches]


        return render_template('TasteBuds.html', matches=results)


    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
