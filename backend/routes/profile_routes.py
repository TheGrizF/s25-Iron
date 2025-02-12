from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from database.models import User, TasteProfile
from database import db

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
def view_profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Log in to view profile.', 'error')
        return redirect(url_for('auth.index'))
    
    user = User.query.get(user_id)
    return render_template('profile.html', user=user)

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

@profile_bp.route('/taste-profile')
def taste_profile():
    return render_template('tasteProfile.html')

@profile_bp.route('/api/taste-profile', methods=['POST'])
def save_taste_profile():
    try:
        data = request.get_json()
        taste_profile = TasteProfile(
            dietaryRestrictions=data['dietaryRestrictions'],
            sweet=data['tasteScores']['sweet'],
            salty=data['tasteScores']['salty'],
            sour=data['tasteScores']['sour'],
            bitter=data['tasteScores']['bitter'],
            umami=data['tasteScores']['umami']
        )

        db.session.add(taste_profile)
        db.session.commit()

        user = User.query.get(data['userId'])
        user.tasteProfileID = taste_profile.tasteProfileID
        db.session.commit()

        return jsonify({'success': True}), 200

    except Exception as e:
        print(f"Error saving taste profile: {str(e)}")
        return jsonify({'error': 'Failed to save taste profile'}), 500