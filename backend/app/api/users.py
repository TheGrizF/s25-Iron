from flask import jsonify, request
from ..models import db, User
from . import bp

@bp.route('/test', methods=['GET'])
def test_route():
    return jsonify({"message": "API is working!"})

@bp.route('/get_by_email', methods=['GET'])
def get_user_by_email():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({
            'firstName': user.firstName,
            'lastName': user.lastName,
            'email': user.email
        }), 200
    else:
        return jsonify({'error': 'User not found'}), 404

@bp.route('/user', methods=['GET'])
def get_user():
    # Fetch a mock user (later a real one?)
    user = {'username': 'Dr. SMock'}
    return jsonify(user)


@bp.route('/add', methods=['POST'])
def add_user():
    data = request.get_json()
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    email = data.get('email')

    if not first_name or not last_name or not email:
        return jsonify({'error': 'Invalid data'}), 400
    
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'User already exists'}), 409

    # Add user to the database
    new_user = User(firstName=first_name, lastName=last_name, email=email)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User added successfully'}), 201