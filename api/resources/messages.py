from flask_restful import Resource, request
from flask import jsonify, session
from repositories.messages_repository import MessagesRepository


class Messages(Resource):
    def get(self, room_id):
        messages = MessagesRepository().get_last_50_messages_by_room_id(room_id)
        return jsonify([{
            'user': message.user,
            'message': message.message,
            'timestamp': message.timestamp.isoformat()
        } for message in messages])
    
    def post(self, room_id):
        data = request.json
        message = data.get('message')
        username = session.get('username')
        
        room = RoomRepository().get_detail_by_id(room_id)
        if not room:
            return jsonify({'success': False, 'message': 'Room does not exist'})
        
        new_message = Messages(room_id=room_id, user=username, message=message)
        db.session.add(new_message)
        db.session.commit()
        
        return jsonify({'success': True})