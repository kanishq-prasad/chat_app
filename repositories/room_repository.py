# taken from room_manager.py in models folder
# needs to be replaced by chat_repository.py in future
from database.db import safe_session
from models.rooms import Rooms
from repositories.base_repository import BaseRepository
import logging


logger = logging.getLogger(__name__)

class RoomRepository(BaseRepository, Rooms):
    """
    This class is responsible for handling all the database operations related to the Rooms model.
    BaseRepository is inherited to use the _save_in_db method to save the message to the database.
    """
    
    def create_room(self, room_name):
        new_room = Rooms(room_name=room_name)
        try:
            with safe_session() as session:
                session.add(new_room)
                session.commit()
                return new_room.id
        except Exception as e:
            logger.error("Error in creating room '%s': %s", room_name, e)
            return False
        
    def get_room_name_by_id(self, room_id):
        try:
            with safe_session() as session:
                room = session.query(Rooms).filter(Rooms.id == room_id).first()
                room = room.to_dict()
                return room['room_name']
        except Exception as e:
            logger.error("Error in getting room by id: %s", e)
            return False
    
    def get_rooms_by_ids(self, room_ids):
        try:
            with safe_session() as session:
                room_details = session.query(Rooms).filter(Rooms.id.in_(room_ids)).all()
                room_details = [room.to_dict() for room in room_details]
                return room_details
        except Exception as e:
            logger.error("Error in getting message details by ids: %s", e)
            return False
        
    def check_room_exists(self, room_id):
        try:
            with safe_session() as session:
                room = session.query(Rooms).filter(Rooms.id == room_id).first()
                room = room.to_dict()
                return room
        except Exception as e:
            logger.error("Error in checking room exists: %s", e)
            return False