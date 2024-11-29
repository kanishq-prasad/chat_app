from flask_restful import Resource
from flask import jsonify, session
from repositories.user_rooms_repository import UserRoomsRepository


class UserRooms(Resource):
    def post(self, data):
        user_id = data.get('user_id')
        room_id = data.get('room_id')

        user_room_id = UserRoomsRepository().create_user_room(user_id, room_id)

        if not room_id:
            return jsonify({'success': False, 'message': 'Error creating user room'})
        return jsonify({'success': True, 'room_id': user_room_id})