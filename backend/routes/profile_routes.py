from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from database.models.dish import dish, menu, menuDishJunction
from database.models.restaurant import restaurant, operatingHours, liveUpdate
from database.models.review import review
from database.models.taste_profiles import tasteProfile, dishTasteProfile
from database.models.user import user, tasteComparisons, cuisine, cuisineUserJunction, friends, savedDishes, savedRestaurants, user_allergen, user_restriction
from database.tasteMatching import updateTasteComparisons
from database import db
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

    return render_template('profile.html', user=selected_user, friendsList=friendsList)


@profile_bp.route('/userProfile/<user_id>')
def viewUserProfile(user_id):
    selected_user = user.query.get(user_id)
    return render_template('userProfile.html', user=selected_user)

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
    return render_template('tasteProfile.html')

@profile_bp.route('/taste-profile/step2')
def taste_profile_step2():
    return render_template('tasteProfile2.html')

@profile_bp.route('/taste-profile/step3')
def taste_profile_step3():
    return render_template('tasteProfile3.html')

@profile_bp.route('/taste-profile/step4')
def taste_profile_step4():
    return render_template('tasteProfile4.html')

@profile_bp.route('/taste-profile/step5')
def taste_profile_step5():
    return render_template('tasteProfile5.html')

@profile_bp.route('/taste-profile/step6')
def taste_profile_step6():
    return render_template('tasteProfile6.html')

@profile_bp.route('/taste-profile/step7')
def taste_profile_step7():
    return render_template('tasteProfile7.html')

@profile_bp.route('/taste-profile/step8')
def taste_profile_step8():
    return render_template('tasteProfile8.html')

@profile_bp.route('/taste-profile/step9')
def taste_profile_step9():
    return render_template('tasteProfile9.html')

@profile_bp.route('/taste-profile/step10')
def taste_profile_step10():
    return render_template('tasteProfile10.html')

@profile_bp.route('/taste-profile/step11')
def taste_profile_step11():
    return render_template('tasteProfile11.html')

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
        
        # Store the data in session
        session['taste_profile_step1'] = data
        session.modified = True  # Explicitly mark the session as modified
        
        return jsonify({'status': 'success'})
    except Exception as e:
        print("Error:", str(e))  # Debug log
        return jsonify({'status': 'error', 'message': str(e)}), 500

@profile_bp.route('/api/taste-profile/step2', methods=['POST'])
def save_taste_profile_step2():
    try:
        data = request.get_json()
        session['taste_profile_step2'] = data
        session.modified = True
        return jsonify({'status': 'success'})
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500

@profile_bp.route('/api/taste-profile/step3', methods=['POST'])
def save_taste_profile_step3():
    try:
        data = request.get_json()
        session['taste_profile_step3'] = data
        session.modified = True
        return jsonify({'status': 'success'})
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500

@profile_bp.route('/api/taste-profile/step4', methods=['POST'])
def save_taste_profile_step4():
    try:
        data = request.get_json()
        session['taste_profile_step4'] = data
        session.modified = True
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
        return jsonify({'status': 'success'})
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
@profile_bp.route('/api/taste-profile/save', methods=['POST'])
def save_taste_profile():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'user not logged in'}), 401

        data = {}
        for i in range(1, 12):
            key = f'taste_profile_step{i}'
            data.update(session.get(key, {}))

        selected_user = user.query.get(user_id)

        if not selected_user:
            return jsonify({'status': 'error', 'message': 'user not found'}), 404

        taste_profile = selected_user.taste_profile
        
        if not taste_profile:
            taste_profile = tasteProfile(user_id=user_id)
            selected_user.taste_profile = taste_profile
            db.session.add(taste_profile)
        else:
            taste_profile.user_id = user_id
        
        # Clear existing allergens and restrictions
        db.session.query(user_allergen).filter_by(user_id=user_id).delete()
        db.session.query(user_restriction).filter_by(user_id=user_id).delete()

        # Add new allergens
        for allergen in data.get('allergens', []):
            print(allergen)
            new_allergen = user_allergen(user_id=user_id, allergen=allergen)
            db.session.add(new_allergen)

        # Add other allergens
        other_allergies = data.get('otherAllergies', [])
        for other_allergy in other_allergies:
            other_allergy = other_allergy.lower()  # Convert to lowercase
            print(other_allergy)
            new_allergen = user_allergen(user_id=user_id, allergen=other_allergy)
            db.session.add(new_allergen)

        # Add new restrictions
        for restriction in data.get('diets', []):
            print(restriction)
            new_restriction = user_restriction(user_id=user_id, restriction=restriction)
            db.session.add(new_restriction)
            
        taste_profile.sweet = data.get('sweet', 3)
        taste_profile.savory = data.get('savory', 3)
        taste_profile.sour = data.get('sour', 3)
        taste_profile.bitter = data.get('bitter', 3)
        taste_profile.spicy = data.get('spicy', 3)
        taste_profile.umami = data.get('umami', 3)

        db.session.commit()

        # trigger taste matching
        updateTasteComparisons(user_id)

        # Clear data
        for i in range(1, 12):
            session.pop(f'taste_profile_step{i}', None)
        flash('Taste Profile Saved!', 'success')
        return jsonify({'status': 'success'})
    
    except Exception as e:
        db.session.rollback()
        print(f"Error in save_taste_profile: {str(e)}")  # Add this line to log the error
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
@profile_bp.route('/matches', methods=['GET'])
def matches_page():
    try:
        user_id = session.get('user_id')
        selected_user = user.query.get(user_id)

        if selected_user:
            return render_template('tasteMatches.html', user_name=f"{selected_user.first_name} {selected_user.last_name}")
        else:
            return render_template("matches.html", user_name="Your")
    except Exception as e:
        print(f"Error in matches_page: {e}")
        return render_template("matches.html", user_name="Your")

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
