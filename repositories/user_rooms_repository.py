from database.db import safe_session
from models.user_rooms import UserRooms
from repositories.base_repository import BaseRepository
import logging


logger = logging.getLogger(__name__)

class UserRoomsRepository(BaseRepository):
    """
    This class is responsible for handling all the database operations related to the User model.
    BaseRepository is inherited to use the _save_in_db method to save the message to the database.
    """

    def create_user_room(self, user_id, room_id):
        new_user_rooms = UserRooms(user_id=user_id, room_id=room_id)
        try:
            with safe_session() as session:
                session.add(new_user_rooms)
                session.commit()
                return new_user_rooms.id
        except Exception as e:
            logger.error("Error in creating user_rooms '%s': %s", user_id, e)
            return False
    
    def get_all_rooms_by_user_id(self, user_id):
        try:
            with safe_session() as session:
                user_rooms = session.query(UserRooms).filter_by(user_id=user_id).all()
                user_rooms = [user_room.to_dict() for user_room in user_rooms]
                return user_rooms
        except Exception as e:
            logger.error("Error in getting user_rooms by user id: %s", e)
            return False