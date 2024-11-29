from flask_restful import Resource
from flask import jsonify, session
from repositories.room_repository import RoomRepository


class Rooms(Resource):
    def join(self, data):
        room_id = data['roomID']
        user_id = data['user_id']
        
        existing_room = RoomRepository().check_room_exists(room_id)
        if not existing_room:
            return jsonify({'success': False, 'message': 'Room not found'})
        
        session['user_id'] = user_id
        session['room_id'] = room_id
        session['messages'] = []
        return jsonify({'success': True, 'room_id': room_id})

    def get(self, room_id):
        room_name = RoomRepository().get_room_name_by_id(room_id)
        if room_name:
            return room_name
        return False
    
    def post(self, data):
        room_name = data.get('roomName')
        user_id = data.get('user_id')

        room_id = RoomRepository().create_room(room_name)
        
        session['user_id'] = user_id
        session['room_id'] = room_id
        if not room_id:
            return jsonify({'success': False, 'message': 'Error creating room'})
        return jsonify({'success': True, 'room_id': room_id})