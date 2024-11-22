from datetime import datetime
from flask import request
from flask_socketio import join_room, leave_room
from app import app, socketio, db
from models.rooms import Rooms
from models.messages import Messages
from models.room_manager import RoomManager


# Initialize room manager
room_manager = RoomManager()

@socketio.on('join')
def on_join(data):
    room = data['room']
    username = data['username']
    join_room(room)
    
    # Handle both in-memory and database operations
    room_manager.join_room(room, username)
    
    with app.app_context():
        # Create or update room in database
        room_obj = Rooms.query.filter_by(room_code=room).first()
        if not room_obj:
            room_obj = Rooms(room_code=room)
            db.session.add(room_obj)
        room_obj.last_activity = datetime.utcnow()
        db.session.commit()
        
        # Load recent messages
        messages = Messages.query.filter_by(room_code=room)\
            .order_by(Messages.created_at.desc())\
            .limit(50)\
            .all()
        
        # Emit message history
        for msg in reversed(messages):
            socketio.emit('message', {
                'username': msg.username,
                'message': msg.content,
                'timestamp': msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }, room=room, to=request.sid)
    
    socketio.emit('status', {'msg': f'{username} has joined the room.'}, room=room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    username = data['username']
    leave_room(room)
    
    # Handle both in-memory and database operations
    room_manager.leave_room(room, username)
    
    # Update active users list
    active_users = room_manager.get_active_users(room)
    socketio.emit('active_users', {'users': active_users}, room=room)
    
    socketio.emit('status', {'msg': f'{username} has left the room.'}, room=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
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
        room_obj = Rooms.query.filter_by(room_code=room).first()
        if room_obj:
            room_obj.last_activity = datetime.utcnow()
        
        db.session.commit()
        
        # Emit message with timestamp
        socketio.emit('message', {
            'username': username,
            'message': message_content,
            'timestamp': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }, room=room)

