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
        print("Received data:", data)  # Debug log
        
        # Store the data in session
        session['taste_profile_step1'] = data
        session.modified = True  # Explicitly mark the session as modified
        
        print("Session after storage:", dict(session))  # Debug log
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