
from flask import Blueprint, request, jsonify
from models import mongo
from datetime import datetime, timedelta
import bcrypt
import jwt
from bson import ObjectId
from config import Config

users_bp = Blueprint('users', __name__)


def generate_token(user_id):
    payload = {
        'user_id': str(user_id),
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')


def get_user_from_token():
    token = request.headers.get('Authorization')
    if not token:
        return None

    if token.startswith('Bearer '):
        token = token[7:]

    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        return user
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Exception):
        return None


def convert_objectids(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectids(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectids(v) for v in obj]
    else:
        return obj


@users_bp.route('/users/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        if not data.get('name') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Name, email and password are required'}), 400

        existing_user = mongo.db.users.find_one({'email': data['email']})
        if existing_user:
            return jsonify({'error': 'User already exists with this email'}), 400

        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

        user_data = {
            'name': data['name'],
            'email': data['email'],
            'password': hashed_password,
            'preferences': data.get('preferences', {}),
            'saved_packages': [],
            'package_history': [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        result = mongo.db.users.insert_one(user_data)
        token = generate_token(result.inserted_id)

        user_response = {
            '_id': str(result.inserted_id),
            'name': user_data['name'],
            'email': user_data['email'],
            'preferences': user_data['preferences'],
            'created_at': user_data['created_at']
        }

        return jsonify({
            'message': 'User registered successfully',
            'user': user_response,
            'token': token
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/users/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400

        user = mongo.db.users.find_one({'email': data['email']})
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401

        if not bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
            return jsonify({'error': 'Invalid email or password'}), 401

        token = generate_token(user['_id'])

        user_data = {
            '_id': str(user['_id']),
            'name': user['name'],
            'email': user['email'],
            'preferences': user.get('preferences', {}),
            'saved_packages': user.get('saved_packages', []),
            'created_at': user['created_at']
        }

        return jsonify({
            'message': 'Login successful',
            'user': user_data,
            'token': token
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/users/me', methods=['GET'])
def get_current_user():
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Invalid or expired token'}), 401

        user_data = {
            '_id': str(user['_id']),
            'name': user['name'],
            'email': user['email'],
            'preferences': user.get('preferences', {}),
            'saved_packages': user.get('saved_packages', []),
            'created_at': user['created_at']
        }

        return jsonify({
            'success': True,
            'user': user_data
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/users/saved-packages', methods=['POST'])
def save_package():
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Invalid or expired token'}), 401

        data = request.get_json()
        if 'package_id' not in data:
            return jsonify({'error': 'Package ID is required'}), 400

        package = mongo.db.packages.find_one({'_id': ObjectId(data['package_id'])})
        if not package:
            return jsonify({'error': 'Package not found'}), 404

        result = mongo.db.users.update_one(
            {'_id': user['_id']},
            {
                '$addToSet': {'saved_packages': data['package_id']},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )

        if result.modified_count == 0:
            return jsonify({'error': 'Package already saved or user not found'}), 400

        return jsonify({'message': 'Package saved successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/users/saved-packages', methods=['GET'])
def get_saved_packages():
    try:
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'Invalid or expired token'}), 401

        saved_packages_ids = user.get('saved_packages', [])
        packages = []

        for package_id in saved_packages_ids:
            try:
                package = mongo.db.packages.find_one({'_id': ObjectId(package_id)})
                if package:
                    package = convert_objectids(package)
                    packages.append(package)
            except:
                continue

        return jsonify({
            'success': True,
            'count': len(packages),
            'packages': packages
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500