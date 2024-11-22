from flask import Blueprint, render_template, request, session, redirect
from api.resources.rooms import Rooms
from api.resources.messages import Messages

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/')
def index():
    return render_template('index.html')

@chat_bp.route('/create-room', methods=['POST'])
def create_room():
    data = request.json
    return Rooms().post(data)

@chat_bp.route('/join-room', methods=['POST'])
def join_room():
    data = request.json
    return Rooms().join(data)

@chat_bp.route('/chat/<room_id>')
def chat(room_id):
    if 'username' not in session:
        return redirect('/')
    
    room_name = Rooms().get(room_id)
    if not room_name:
        return redirect('/')
    
    return render_template('chat.html', 
                         room_name=room_name,
                         room_id=room_id, 
                         username=session.get('username'))

@chat_bp.route('/chat/<chat_room>', methods=['GET'])
def fetch_messages(room_code):
    return Messages().get(room_code)