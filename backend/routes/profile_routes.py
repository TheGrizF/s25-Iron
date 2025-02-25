from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from database.models import User, TasteProfile, TasteComparison, TasteBuddies
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
    
    user = User.query.get(user_id)
    #fetch information on friends
    friendsList = db.session.query(TasteBuddies, User).join(User, TasteBuddies.buddyID == User.userID).filter(TasteBuddies.userID==user_id).all()
    friendsData = [{
        'buddyID': friend.User.userID,
        'firstName': friend.User.firstName,
        'lastName' : friend.User.lastName,
    } for friend in friendsList]

    return render_template('profile.html', user=user, friendsList=friendsData)


@profile_bp.route('/userProfile/<user_id>')
def viewUserProfile(user_id):
    user = User.query.get(user_id)
    return render_template('userProfile.html', user=user)

@profile_bp.route('/delete_profile', methods=['POST'])
def delete_profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('You are not logged in.', 'error')
        return redirect(url_for('auth.index'))
    
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        session.clear()
        flash('Profile successfully deleted.', 'success')
    else:
        flash('User not found?', 'error')
    
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
            return jsonify({'status': 'error', 'message': 'User not logged in'}), 401

        data = {}
        for i in range(1, 12):
            key = f'taste_profile_step{i}'
            data.update(session.get(key, {}))

        user = User.query.get(user_id)

        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        taste_profile = user.taste_profile
        
        if not taste_profile:
            taste_profile = TasteProfile(userID=user_id)
            user.taste_profile = taste_profile
            db.session.add(taste_profile)
        else:
            taste_profile.userID = user_id

        # Add allergies to Dietary Restrictions
        diet_allergy = {
            "dietaryRestrictions": data.get('diets', []),
            "allergies": data.get('allergens', [])
        }

        taste_profile.dietaryRestrictions = json.dumps(diet_allergy)
        taste_profile.sweet = data.get('sweet', 3)
        taste_profile.spicy = data.get('spicy', 3)
        taste_profile.sour = data.get('sour', 3)
        taste_profile.bitter = data.get('bitter', 3)
        taste_profile.umami = data.get('umami', 3)
        taste_profile.savory = data.get('savory', 3)

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
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
@profile_bp.route('/matches', methods=['GET'])
def matches_page():
    try:
        user_id = session.get('user_id')
        user = User.query.get(user_id)

        return render_template('tasteMatches.html', user_name=f"{user.firstName} {user.lastName}")
    except Exception as e:
        print(f"Error in matches_page: {e}")
        return render_template("matches.html", user_name="Your")

@profile_bp.route('/api/taste-profile/matches', methods=['GET'])
def get_user_matches():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'User not logged in'}), 401

        matches = db.session.query(
            TasteComparison.compareTo,
            User.firstName,
            User.lastName,
            TasteComparison.comparisonNum
        ).join(User, User.userID == TasteComparison.compareTo).filter(
            TasteComparison.compareFrom == user_id
        ).order_by(TasteComparison.comparisonNum).all()

        results = [{"userID": match.compareTo, 
                    "name": f"{match.firstName} {match.lastName}",
                    "comparisonNum": match.comparisonNum} 
                    for match in matches]

        return jsonify({'status': 'success', 'matches': results}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
