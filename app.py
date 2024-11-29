from flask import Flask, request
from flask_socketio import SocketIO, join_room, leave_room
from config import Config
from api.chat_routes import chat_bp
from database.db import db
from datetime import datetime
from models.rooms import Rooms
from repositories.user_repository import UserRepository
from models.messages import Messages
from models.room_manager import RoomManager


app = Flask(__name__)
app.config.from_object(Config)

# Register blueprints
app.register_blueprint(chat_bp)

# Initialize extensions
db.init_app(app)
socketio = SocketIO(app)

# Create database tables
with app.app_context():
    db.create_all()

# import socket_events
room_manager = RoomManager()

@socketio.on('join') # works for both join room and create room
def on_join(data):
    print("data in socketio.on('join')", data)
    room = data['room']
    user_id = data['user_id']
    join_room(room)
    
    # Handle both in-memory and database operations
    room_manager.join_room(room, user_id)
    
    with app.app_context():
        # Create or update room in database
        room_obj = Rooms.query.filter_by(id=room).first()
        if not room_obj:
            room_obj = Rooms(id=room)
            db.session.add(room_obj)
        room_obj.last_activity = datetime.utcnow()
        db.session.commit()
        
        # Load recent messages
        messages = Messages.query.filter_by(room_id=room)\
            .order_by(Messages.created_at.desc())\
            .limit(50)\
            .all()
        
        usernames = UserRepository().get_usernames_by_ids([msg.user_id for msg in reversed(messages)])

        # Emit message history
        i = 0
        for msg in reversed(messages):
            socketio.emit('message', {
                'username': usernames[msg.user_id],
                'message': msg.content,
                'timestamp': msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }, room=room, to=request.sid)
            i += 1
    
    # Update active users list
    active_users = room_manager.get_active_users(room)
    # print("active users", active_users)
    active_usernames = UserRepository().get_usernames_by_ids(list(active_users))
    socketio.emit('active_users', {'users': active_usernames}, room=room)
    
    socketio.emit('status', {'msg': f'{user_id} has joined the room.'}, room=room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    user_id = data['user_id']
    leave_room(room)

    username = UserRepository().get_username_by_id(user_id)
    
    # Handle both in-memory and database operations
    room_manager.leave_room(room, user_id)
    
    # Update active users list
    active_users = room_manager.get_active_users(room)
    # print("active users", active_users)
    active_usernames = UserRepository().get_usernames_by_ids(list(active_users))
    socketio.emit('active_users', {'users': active_usernames}, room=room)
    
    socketio.emit('status', {'msg': f'{username} has left the room.'}, room=room)

@socketio.on('message')
def handle_message(data):
    room_id = data['room_id']
    user_id = data['user_id']
    message_content = data['message']
    
    # Save message to database
    with app.app_context():
        message = Messages(
            room_id=room_id,
            user_id=user_id,
            content=message_content
        )
        db.session.add(message)
        
        # Update room's last activity
        room_obj = Rooms.query.filter_by(id=room_id).first()
        if room_obj:
            room_obj.last_activity = datetime.utcnow()
        
        db.session.commit()

        username = UserRepository().get_username_by_id(user_id)
        
        # Emit message with timestamp
        socketio.emit('message', {
            'username': username,
            'message': message_content,
            'timestamp': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }, room=room_id)

if __name__ == '__main__':
    socketio.run(app, debug=True)