from flask import Blueprint, jsonify, render_template, request, session, redirect
from api.resources.rooms import Rooms
from api.resources.messages import Messages
from api.resources.user_rooms import UserRooms
from database.db import db
from models.users import Users
from repositories.user_repository import UserRepository
from repositories.user_rooms_repository import UserRoomsRepository
from repositories.room_repository import RoomRepository
from utils.auth import generate_token, token_required

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/')
def index():
    return render_template('index.html')

@chat_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    # print(username, password, "username and password")
    print(data, "data in register")
    username = data.get('username')
    password = data.get('password')
    
    # Validate input
    if not username or not password:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    # Check if user already exists
    existing_user = Users.query.filter((Users.username == username)).first()
    if existing_user:
        return jsonify({'success': False, 'message': 'Username or email already exists'}), 400
    
    # Create new user
    new_user = Users(username=username)
    new_user.set_password(password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        
        # Generate JWT token
        token = generate_token(new_user)
        
        return jsonify({
            'success': True, 
            'message': 'User registered successfully',
            'token': token,
            'user_id': new_user.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@chat_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    print(data, "data in login")
    username = data.get('username')
    password = data.get('password')
    print(username, password, "username and password")
    
    # Find user
    user = Users.query.filter_by(username=username).first()
    
    # Validate credentials
    if user and user.check_password(password):
        # Generate JWT token
        token = generate_token(user)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user_id': user.id
        }), 200
    
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@chat_bp.route('/rooms/<user_id>', methods=['GET'])
# @token_required
def rooms(user_id):
    username = UserRepository().get_username_by_id(user_id)
    user_rooms = UserRoomsRepository().get_all_rooms_by_user_id(user_id)
    user_rooms = [room['room_id'] for room in user_rooms]
    # print(user_rooms, "user_rooms")
    rooms = RoomRepository().get_rooms_by_ids(user_rooms)
    rooms = [
                {
                    'room_id': str(room['id']),  # Ensure room_id is a string
                    'room_name': room['room_name']
                }
                for room in rooms
            ]
    # print(rooms, "rooms")
    
    return render_template('user_room.html',
                           username=username,
                           user_id=user_id,
                           rooms=rooms)

@chat_bp.route('/add-room/<user_id>')
# @token_required
def add_room(user_id):
    # username = UserRepository().get_username_by_id(user_id)
    return render_template('add_room.html',
                           user_id=user_id)

@chat_bp.route('/create-room', methods=['POST', 'GET'])
# @token_required
def create_room():
    data = request.json
    response = Rooms().post(data).json
    print(response.get('success'), "response in create_room")
    if response.get('success'):
        data['room_id'] = response.get('room_id')
        return UserRooms().post(data).json
    else:
        return response

@chat_bp.route('/join-room', methods=['POST'])
# @token_required
def join_room():
    data = request.json
    # print(data, "data in join_room, chat_routes")
    response = Rooms().join(data).json
    print(response.get('success'), "response in join_room")
    if response.get('success'):
        data['room_id'] = response.get('room_id')
        return UserRooms().post(data)
    else:
        return response

@chat_bp.route('/chat/<user_id>/<room_id>')
# @token_required
def chat(user_id, room_id):

    data = {
        'room_id': room_id,
        'user_id': user_id
    }

    Rooms().join(data)
    
    # print(user_id, room_id, "user_id and room_id in chat route")
    
    room_name = Rooms().get(room_id)
    username = UserRepository().get_username_by_id(user_id)
    if not room_name:
        return redirect('/')
    
    return render_template('chat_room.html', 
                         room_name=room_name,
                         room_id=room_id, 
                         username=username,
                         user_id=session.get('user_id'))

@chat_bp.route('/chat/<chat_room>', methods=['GET'])
# @token_required
def fetch_messages(room_code):
    return Messages().get(room_code)