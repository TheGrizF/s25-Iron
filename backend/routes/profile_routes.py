from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from backend.utils import get_dish_recommendations
from database.models.dish import dish, menu, menuDishJunction
from database.models.restaurant import restaurant, operatingHours, liveUpdate
from database.models.review import review
from database.models.taste_profiles import tasteProfile, dishTasteProfile
from database.models.user import user, tasteComparisons, cuisine, cuisineUserJunction, friends, savedDishes, savedRestaurants, user_allergen, user_restriction
from database.tasteMatching import updateTasteComparisons
from database import db
from sqlalchemy.orm import joinedload, contains_eager # Add contains_eager
import json

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
def view_profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Log in to view profile.', 'error')
        return redirect(url_for('auth.index'))
    
    selected_user = user.query.get(user_id)

    #fetch information on friends
    friendsList = db.session.query(user).join(friends, friends.buddy_id == user.user_id).filter(friends.user_id==user_id).all()

    # Get taste matches
    matches = db.session.query(
        tasteComparisons.compare_to,
        user.first_name,
        user.last_name,
        tasteComparisons.comparison_num,
        user.icon_path
    ).join(user, user.user_id == tasteComparisons.compare_to).filter(
        tasteComparisons.compare_from == user_id
    ).order_by(tasteComparisons.comparison_num).limit(5).all()

    taste_matches = [{"user_id": match.compare_to, 
                    "name": f"{match.first_name} {match.last_name}",
                    "comparison_num": match.comparison_num,
                    "icon_path": match.icon_path} 
                    for match in matches]

    # Get recommended dishes
    recommended_dishes = get_dish_recommendations(user_id)[:5]
    dish_matches = []
    for dish_id, buddy_id, match_percent in recommended_dishes:
        dish_info = db.session.query(dish.dish_name).filter(dish.dish_id == dish_id).first()
        buddy_info = db.session.query(user.first_name, user.last_name).filter(user.user_id == buddy_id).first()

        dish_matches.append({
            'dish_id': dish_id,
            'dish_name': dish_info.dish_name,
            'buddy_name': f"{buddy_info.first_name} {buddy_info.last_name}",
            'match_percent': match_percent
        })

    return render_template('profile.html', 
                         user=selected_user, 
                         friendsList=friendsList,
                         taste_matches=taste_matches,
                         dish_matches=dish_matches)

@profile_bp.route('/user/<user_id>')
def viewUserSearchResults(user_id):
    selected_user = user.query.get(user_id)
    # Kept if we want to use it to return search results for all users that fall under the query instead of one)
    # return render_template('userSearchResult.html', user=selected_user) 
    return render_template('user.html', viewed_user=selected_user)

@profile_bp.route('/delete_profile', methods=['POST'])
def delete_profile():
    user_id = session.get('user_id')

    if not user_id:
        flash('You are not logged in.', 'error')
        return redirect(url_for('auth.index'))
    
    selected_user = user.query.get(user_id)

    if not selected_user:
        flash('User not found.', 'error')
        return redirect(url_for('auth.index'))

    try:
        db.session.delete(selected_user)
        db.session.commit()
        session.clear()
        flash('Profile successfully deleted.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting profile: {str(e)}', 'error')

    return redirect(url_for('auth.index'))

@profile_bp.route('/taste-profile', methods=['GET', 'POST'])
def taste_profile():
    if request.method == 'POST':
        return redirect(url_for('profile.taste_profile_step2'))
    return render_template('tasteProfile.html', current_step=1)

@profile_bp.route('/taste-profile/step2')
def taste_profile_step2():
    return render_template('tasteProfile2.html', current_step=2)

@profile_bp.route('/taste-profile/step3')
def taste_profile_step3():
    return render_template('tasteProfile3.html', current_step=3)

@profile_bp.route('/taste-profile/step4')
def taste_profile_step4():
    return render_template('tasteProfile4.html', current_step=4)

@profile_bp.route('/taste-profile/step5')
def taste_profile_step5():
    return render_template('tasteProfile5.html', current_step=5)

@profile_bp.route('/taste-profile/step6')
def taste_profile_step6():
    return render_template('tasteProfile6.html', current_step=6)

@profile_bp.route('/taste-profile/step7')
def taste_profile_step7():
    return render_template('tasteProfile7.html', current_step=7)

@profile_bp.route('/taste-profile/step8')
def taste_profile_step8():
    return render_template('tasteProfile8.html', current_step=8)

@profile_bp.route('/taste-profile/step9')
def taste_profile_step9():
    return render_template('tasteProfile9.html', current_step=9)

@profile_bp.route('/taste-profile/step10')
def taste_profile_step10():
    return render_template('tasteProfile10.html', current_step=10)

@profile_bp.route('/taste-profile/step11')
def taste_profile_step11():
    return render_template('tasteProfile11.html', current_step=11)

@profile_bp.route('/taste-profile/debug')
def taste_profile_debug():
    print("Full session contents:", dict(session))
    for i in range(1, 12):
        key = f'taste_profile_step{i}'
        print(f"Step {i} data:", session.get(key))
    return render_template('tasteProfileDebug.html')

@profile_bp.route('/api/taste-profile/step1', methods=['POST'])
def save_taste_profile_step1():
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        # Store the data in session
        session['taste_profile_step1'] = data
        session.modified = True  # Explicitly mark the session as modified

        fav_restaurant = data.get('favoriteRestaurant', '').strip()
        print(fav_restaurant)
        fav_dish = data.get('favoriteDish', '').strip()

        taste_profile = tasteProfile.query.filter_by(user_id=user_id).first()
        if not taste_profile:
            taste_profile = tasteProfile(user_id=user_id)
            db.session.add(taste_profile)

        if fav_restaurant:
            rest_match = restaurant.query.filter(
                restaurant.restaurant_name.ilike(fav_restaurant)
            ).first()
            if rest_match:
                fav_cuisine = rest_match.cuisine

                cuisine_obj = db.session.query(cuisine).filter_by(cuisine_name=fav_cuisine).first()
                add_cuisine = cuisineUserJunction(
                    user_id=user_id,
                    cuisine_id=cuisine_obj.cuisine_id,
                    preference_level=5
                )
                db.session.add(add_cuisine)

        if fav_dish:
            dish_match = dish.query.filter(
                dish.dish_name.ilike(fav_dish)
            ).first()
            if dish_match:
                dish_profile = db.session.query(dishTasteProfile).filter_by(dish_id=dish_match.dish_id).first()
                if dish_profile:
                    taste_profile.sweet = dish_profile.sweet
                    taste_profile.savory = dish_profile.savory
                    taste_profile.sour = dish_profile.sour
                    taste_profile.bitter = dish_profile.bitter
                    taste_profile.spicy = dish_profile.spicy
                    taste_profile.umami = dish_profile.umami

                saved = savedDishes(user_id=user_id, dish_id=dish_match.dish_id)
                db.session.add(saved)


        taste_profile.current_step=1
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        print("Error:", str(e))  # Debug log
        return jsonify({'status': 'error', 'message': str(e)}), 500

@profile_bp.route('/api/taste-profile/step2', methods=['POST'])
def save_taste_profile_step2():
    try:
        data = request.get_json()
        session['taste_profile_step2'] = data
        session.modified = True

        user_id = session.get('user_id')
        taste_profile = tasteProfile.query.filter_by(user_id=user_id).first()
        
        allergens = data.get('allergens', [])
        for allergen in allergens:
            db.session.add(user_allergen(user_id=user_id, allergen=allergen))
        other_allergens = data.get('otherAllergies', [])
        for other in other_allergens:
            db.session.add(user_allergen(user_id=user_id, allergen=other.strip().lower()))

        restrictions = data.get('restrictions', [])
        for restriction in restrictions:
            db.session.add(user_restriction(user_id=user_id, restriction=restriction))

        taste_profile.current_step = 2

        db.session.commit()    

        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        print("Error:", str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500

@profile_bp.route('/api/taste-profile/step3', methods=['POST'])
def save_taste_profile_step3():
    try:
        data = request.get_json()
        session['taste_profile_step3'] = data
        session.modified = True

        user_id = session.get('user_id')
        taste_profile=tasteProfile.query.filter_by(user_id=user_id).first()
        taste_profile.sour = data.get('sour', 0)
        taste_profile.current_step = 3

        db.session.commit()

        return jsonify({'status': 'success'})
    
    except Exception as e:
        print("Error:", str(e))
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@profile_bp.route('/api/taste-profile/step4', methods=['POST'])
def save_taste_profile_step4():
    try:
        data = request.get_json()
        session['taste_profile_step4'] = data
        session.modified = True

        user_id = session.get("user_id")
        taste_profile = tasteProfile.query.filter_by(user_id=user_id).first()
        taste_profile.sweet = data.get('sweet', 0)
        taste_profile.current_step = 4

        db.session.commit()

        return jsonify({'status': 'success'})
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500

@profile_bp.route('/api/taste-profile/step5', methods=['POST'])
def save_taste_profile_step5():
    try:
        data = request.get_json()
        session['taste_profile_step5'] = data
        session.modified = True

        
        user_id = session.get("user_id")
        taste_profile = tasteProfile.query.filter_by(user_id=user_id).first()
        taste_profile.umami = data.get('umami', 0)
        taste_profile.current_step = 5

        db.session.commit()
        
        return jsonify({'status': 'success'})
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500

@profile_bp.route('/api/taste-profile/step6', methods=['POST'])
def save_taste_profile_step6():
    try:
        data = request.get_json()
        session['taste_profile_step6'] = data
        session.modified = True

        
        user_id = session.get("user_id")
        taste_profile = tasteProfile.query.filter_by(user_id=user_id).first()
        taste_profile.savory = data.get('savory', 0)
        taste_profile.current_step = 6

        db.session.commit()
        
        return jsonify({'status': 'success'})
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500

@profile_bp.route('/api/taste-profile/step7', methods=['POST'])
def save_taste_profile_step7():
    try:
        data = request.get_json()
        session['taste_profile_step7'] = data
        session.modified = True

        
        user_id = session.get("user_id")
        taste_profile = tasteProfile.query.filter_by(user_id=user_id).first()
        taste_profile.spicy = data.get('spicy', 0)
        taste_profile.current_step = 7

        db.session.commit()
        
        return jsonify({'status': 'success'})
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500

@profile_bp.route('/api/taste-profile/step8', methods=['POST'])
def save_taste_profile_step8():
    try:
        data = request.get_json()
        session['taste_profile_step8'] = data
        session.modified = True

        
        user_id = session.get("user_id")
        taste_profile = tasteProfile.query.filter_by(user_id=user_id).first()
        taste_profile.bitter = data.get('bitter', 0)
        taste_profile.current_step = 8

        db.session.commit()
        
        return jsonify({'status': 'success'})
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500

@profile_bp.route('/api/taste-profile/step9', methods=['POST'])
def save_taste_profile_step9():
    try:
        data = request.get_json()
        session['taste_profile_step9'] = data
        session.modified = True
        return jsonify({'status': 'success'})
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500

@profile_bp.route('/api/taste-profile/step10', methods=['POST'])
def save_taste_profile_step10():
    try:
        data = request.get_json()
        session['taste_profile_step10'] = data
        session.modified = True

        user_id = session.get('user_id')
        db.session.query(cuisineUserJunction).filter_by(user_id=user_id).delete()

        cuisine_preferences = data.get('cuisines', {})
        for cuisine_name, preference_level in cuisine_preferences.items():
            cuisine_obj = cuisine.query.filter_by(cuisine_name=cuisine_name.title()).first()
            if not cuisine_obj:
                cuisine_obj=cuisine(cuisine_name=cuisine_name.title())
                db.session.add(cuisine_obj)
                db.session.flush()

            cuisine_pref=cuisineUserJunction(
                user_id=user_id,
                cuisine_id=cuisine_obj.cuisine_id,
                preference_level=preference_level
            )
            db.session.add(cuisine_pref)

        taste_profile=tasteProfile.query.filter_by(user_id=user_id).first()
        taste_profile.current_step = 10

        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500

@profile_bp.route('/api/taste-profile/step11', methods=['POST'])
def save_taste_profile_step11():
    try:
        data = request.get_json()
        session['taste_profile_step11'] = data
        session.modified = True

        user_id = session.get('user_id')
        taste_profile = tasteProfile.query.filter_by(user_id=user_id).first()
        taste_profile.current_step = 11

        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
@profile_bp.route('/api/taste-profile/exit_early', methods=['POST'])
def exit_early():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'User not logged in'}), 401

        updateTasteComparisons(user_id)

        return jsonify({'status': 'success', 'message': 'Taste Profile updated'})
    except Exception as e:
        print("Error finalizing taste profile:", str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500

@profile_bp.route('/taste-profile/view')
def view_edit_taste_profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in first.', 'error')
        return redirect(url_for('auth.index'))
    
    this_user = user.query.get(user_id)
    profile = this_user.taste_profile

    next_step = None
    if profile and (not profile.current_step or profile.current_step < 11):
        next_step = profile.current_step + 1 if profile.current_step else 1
        if next_step == 9:
            next_step = 10

    return render_template('viewTasteProfile.html', user=this_user, taste_profile=profile, next_step=next_step)
    
@profile_bp.route('/matches', methods=['GET'])
def matches_page():
    try:
        user_id = session.get('user_id')
        selected_user = user.query.get(user_id)

        if selected_user:
            return render_template('tasteMatches.html', user_name=f"{selected_user.first_name} {selected_user.last_name}")
        else:
            return render_template("tasteMatches.html", user_name="Your")
    except Exception as e:
        print(f"Error in matches_page: {e}")
        return render_template("tasteMatches.html", user_name="Your")

@profile_bp.route('/api/taste-profile/matches', methods=['GET'])
def get_user_matches():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'user not logged in'}), 401

        matches = db.session.query(
            tasteComparisons.compare_to,
            user.first_name,
            user.last_name,
            tasteComparisons.comparison_num
        ).join(user, user.user_id == tasteComparisons.compare_to).filter(
            tasteComparisons.compare_from == user_id
        ).order_by(tasteComparisons.comparison_num).all()

        results = [{"user_id": match.compare_to, 
                    "name": f"{match.first_name} {match.last_name}",
                    "comparison_num": match.comparison_num} 
                    for match in matches]

        return jsonify({'status': 'success', 'matches': results}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@profile_bp.route('/dish-matches', methods=['GET'])
def dish_match_page():
    try:
        user_id = session.get('user_id')
        selected_user = user.query.get(user_id)

        if selected_user:
            return render_template('dishMatches.html', user_name=f"{selected_user.first_name} {selected_user.last_name}")
        else:
            return render_template("dishMatches.html", user_name="Your")
    except Exception as e:
        print(f"Error in dish_matches_page: {e}")
        return render_template("dishMatches.html", user_name="Your")
       
@profile_bp.route('/api/dish-matches', methods=['GET'])
def api_dish_matches():
    user_id = session.get('user_id')

    if not user_id:
            return jsonify({'status': 'error', 'message': 'user not logged in'}), 401
    
    recommended_dishes = get_dish_recommendations(user_id)

    results = []
    for dish_id, buddy_id, match_percent in recommended_dishes:
        dish_info = db.session.query(dish.dish_name).filter(dish.dish_id == dish_id).first()
        buddy_info = db.session.query(user.first_name, user.last_name).filter(user.user_id == buddy_id).first()

        results.append({
            'dish_id': dish_id,
            'dish_name': dish_info.dish_name,
            'buddy_name': f"{buddy_info.first_name} {buddy_info.last_name}",
            'match_percent': match_percent
        })

    return jsonify({'status': 'success', 'matches': results})

@profile_bp.route('/user/<int:user_id>')
def view_user(user_id):
    current_user_id = session.get('user_id')
    if not current_user_id:
        flash('Log in to view profiles.', 'error')
        return redirect(url_for('auth.index'))
    
    viewed_user = user.query.get(user_id)
    if not viewed_user:
        flash('User not found.', 'error')
        return redirect(url_for('profile.view_profile'))

    # check if current user is following the viewed user
    is_buddy = db.session.query(friends).filter(
        friends.user_id == current_user_id,
        friends.buddy_id == user_id
    ).first() is not None

    # get taste comparison
    comparison = db.session.query(tasteComparisons).filter(
        tasteComparisons.compare_from == current_user_id,
        tasteComparisons.compare_to == user_id
    ).first()
    
    comparison_num = comparison.comparison_num if comparison else 12  # 50% fallback

    return render_template(
        'user.html',
        viewed_user=viewed_user,
        is_buddy=is_buddy,
        comparison_num=comparison_num
    )

@profile_bp.route('/add-buddy/<int:buddy_id>', methods=['POST'])
def add_buddy(buddy_id):
    current_user_id = session.get('user_id')
    if not current_user_id:
        flash('Log in to add buddies.', 'error')
        return redirect(url_for('auth.index'))
    
    # Check if already buddies
    existing_buddy = db.session.query(friends).filter(
        friends.user_id == current_user_id,
        friends.buddy_id == buddy_id
    ).first()

    if existing_buddy:
        flash('Already buddies!', 'error')
    else:
        new_friendship = friends(user_id=current_user_id, buddy_id=buddy_id)
        db.session.add(new_friendship)
        try:
            db.session.commit()
            flash('Buddy added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error adding buddy.', 'error')
    
    return redirect(url_for('profile.view_user', user_id=buddy_id))

@profile_bp.route('/api/autocomplete')
def autocomplete():
    query = request.args.get('q', '').lower()
    type = request.args.get('type', '')  # 'restaurant' or 'dish'
    
    if type == 'restaurant':
        results = db.session.query(restaurant).filter(
            restaurant.restaurant_name.ilike(f'%{query}%')
        ).limit(5).all()
        return jsonify([{
            'id': r.restaurant_id,
            'name': r.restaurant_name
        } for r in results])
    
    elif type == 'dish':
        results = db.session.query(dish).filter(
            dish.dish_name.ilike(f'%{query}%')
        ).limit(5).all()
        return jsonify([{
            'id': d.dish_id,
            'name': d.dish_name
        } for d in results])
    
    return jsonify([])

@profile_bp.route('/reviewed-dishes')
def reviewed_dishes():
    user_id = session.get('user_id')
    if not user_id:
        flash('Log in to view your reviewed dishes.', 'error')
        return redirect(url_for('auth.index'))

    user_reviews = review.query.filter_by(user_id=user_id) \
                            .options(joinedload(review.dish), joinedload(review.restaurant)) \
                            .order_by(review.created_at.desc()) \
                            .all()

    # Fetch the user object to pass to the template if needed (e.g., for display name)
    current_user = user.query.get(user_id)

    return render_template('reviewedDishes.html', reviews=user_reviews, user=current_user)

@profile_bp.route('/saved-dishes')
def saved_dishes():
    user_id = session.get('user_id')
    if not user_id:
        flash('Log in to view your saved dishes.', 'error')
        return redirect(url_for('auth.index'))

    # Query saved dishes, joining through to restaurant
    user_saved_dishes = savedDishes.query \
        .filter(savedDishes.user_id == user_id) \
        .join(savedDishes.dish) \
        .outerjoin(dish.menu_dishes).outerjoin(menuDishJunction.menu).outerjoin(menu.restaurant) \
        .options(
            contains_eager(savedDishes.dish)
            .contains_eager(dish.menu_dishes)
            .contains_eager(menuDishJunction.menu)
            .contains_eager(menu.restaurant)
        ) \
        .order_by(savedDishes.date_saved.desc()) \
        .all()

    # The query above loads related data. If a dish isn't on *any* menu,
    # its menu_dishes list will be empty, and restaurant info won't be loaded via the join.
    # The template already has a fallback for this.

    current_user = user.query.get(user_id)

    return render_template('savedDishes.html', saved_dishes=user_saved_dishes, user=current_user)