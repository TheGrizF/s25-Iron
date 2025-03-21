from flask import Blueprint, render_template, session, request
from database import db
from database.models.dish import dish
from database.models.user import friends, user
from backend.utils import get_featured_dishes, get_daily_dishes, get_friend_reviews, get_saved_dishes
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

@daily_dish_bp.route('/createGroup', methods = ['POST'])
def createGroup():
    current_user_id = session.get('user_id') 
    selectedFriends = request.form.getlist("selectedFriends")
    activeGroup = selectedFriends
    activeGroupInfo = user.query.filter(user.user_id.in_(activeGroup)).all()
    
    return render_template('TasteBuds.html', activeGroup = activeGroupInfo)

@daily_dish_bp.route('/restaurant/<id>')
def restaurant_detail(id):
    return render_template('restaurant_detail.html')

@daily_dish_bp.route('/review', methods=['GET', 'POST'])
def review():
    user = {'firstName': 'Person-I-Know'} #Umm, don't know how to connect it with db right now
    return render_template('review.html', user = user)
