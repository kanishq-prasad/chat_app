from database.db import safe_session
from models.users import Users
from repositories.base_repository import BaseRepository
import logging


logger = logging.getLogger(__name__)

class UserRepository(BaseRepository):
    """
    This class is responsible for handling all the database operations related to the User model.
    BaseRepository is inherited to use the _save_in_db method to save the message to the database.
    """

    def create_room(self, username, password_hash):
        new_user = Users(username=username, password_hash=password_hash)
        try:
            with safe_session() as session:
                session.add(new_user)
                session.commit()
                return new_user.id
        except Exception as e:
            logger.error("Error in creating user '%s': %s", username, e)
            return False
    
    def get_username_by_id(self, user_id):
        try:
            with safe_session() as session:
                user = session.query(Users).filter_by(id=user_id).first()
                return user.username
        except Exception as e:
            logger.error("Error in getting user by id: %s", e)
            return False
    
    def get_usernames_by_ids(self, user_ids):
        try:
            with safe_session() as session:
                users = session.query(Users).filter(Users.id.in_(user_ids)).all()
                user_dict = {user.id: user.username for user in users}
                # print(user_dict, "users in get_usernames_by_ids")
                ordered_user_dict = {int(user_id): user_dict[int(user_id)] for user_id in user_ids if int(user_id) in user_dict}
                return ordered_user_dict
        except Exception as e:
            logger.error("Error in getting users by ids: %s", e)
            return False