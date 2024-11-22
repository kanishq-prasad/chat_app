# from flask import Flask
# from flask_socketio import SocketIO, join_room, leave_room
# from config import Config
# from routes.chat_routes import chat_bp

# app = Flask(__name__)
# app.config.from_object(Config)
# socketio = SocketIO(app)

# # Register blueprints
# app.register_blueprint(chat_bp)

# # SocketIO event handlers
# @socketio.on('join')
# def on_join(data):
#     room = data['room']
#     username = data['username']
#     join_room(room)
#     socketio.emit('status', {'msg': f'{username} has joined the room.'}, room=room)

# @socketio.on('leave')
# def on_leave(data):
#     room = data['room']
#     username = data['username']
#     leave_room(room)
#     socketio.emit('status', {'msg': f'{username} has left the room.'}, room=room)

# @socketio.on('message')
# def handle_message(data):
#     room = data['room']
#     username = data['username']
#     message = data['message']
#     socketio.emit('message', {
#         'username': username,
#         'message': message
#     }, room=room)

# if __name__ == '__main__':
#     socketio.run(app, debug=True)

from flask import Flask, request
from flask_socketio import SocketIO, join_room, leave_room
from config import Config
from api.chat_routes import chat_bp
from database.db import db
from datetime import datetime
from models.rooms import Rooms
from repositories.room_repository import RoomRepository
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

@socketio.on('join')
def on_join(data):
    print('Joining room...')
    print(data)
    room_id = data['room_id']
    username = data['username']
    join_room(room_id)
    
    # Handle both in-memory and database operations
    room_manager.join_room(room_id, username)
    
    with app.app_context():
        # Create or update room in database
        room_obj = Rooms.query.filter_by(room_id=room_id).first()
        if not room_obj:
            room_obj = Rooms(room_id=room_id)
            db.session.add(room_obj)
        room_obj.last_activity = datetime.utcnow()
        db.session.commit()
        
        # Load recent messages
        messages = Messages.query.filter_by(room_code=room_id)\
            .order_by(Messages.created_at.desc())\
            .limit(50)\
            .all()
        
        # Emit message history
        for msg in reversed(messages):
            socketio.emit('message', {
                'username': msg.username,
                'message': msg.content,
                'timestamp': msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }, room=room_id, to=request.sid)
    
    socketio.emit('status', {'msg': f'{username} has joined the room.'}, room=room_id)

@socketio.on('leave')
def on_leave(data):
    room = data['room_id']
    username = data['username']
    leave_room(room)
    
    # Handle both in-memory and database operations
    room_manager.leave_room(room, username)
    
    # Update active users list
    # active_users = room_manager.get_active_users(room)
    # socketio.emit('active_users', {'users': active_users}, room=room)
    
    socketio.emit('status', {'msg': f'{username} has left the room.'}, room=room)

@socketio.on('message')
def handle_message(data):
    room = data['room_id']
    username = data['username']
    message_content = data['message']
    
    # Save message to database
    with app.app_context():
        message = Messages(
            room_code=room,
            username=username,
            content=message_content
        )
        db.session.add(message)
        
        # Update room's last activity
        room_obj = Rooms.query.filter_by(room_id=room).first()
        if room_obj:
            room_obj.last_activity = datetime.utcnow()
        
        db.session.commit()
        
        # Emit message with timestamp
        socketio.emit('message', {
            'username': username,
            'message': message_content,
            'timestamp': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }, room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)