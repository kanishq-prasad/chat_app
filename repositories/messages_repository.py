from database.db import safe_session
from models.messages import Messages
from repositories.base_repository import BaseRepository
import logging


logger = logging.getLogger(__name__)

class MessagesRepository(Messages, BaseRepository):
    """
    This class is responsible for handling all the database operations related to the Messages model.
    BaseRepository is inherited to use the _save_in_db method to save the message to the database.
    """
    
    def create_new_message(self, data):
        new_message = Messages(
            chat_id=data.chat_id,
            sender_id=data.sender_id,
            message=data.message,
            is_edited=data.is_edited,
            sent_at=data.sent_at,
        )

        try:
            self.save_in_db(new_message)
            return new_message.id
        except Exception as e:
            logger.error("Error in saving message to db: %s", e)
            return False
    
    def to_dict(self):
        return {
            'id': self.id,
            'room_code': self.room_code,
            'username': self.username,
            'content': self.content,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_message_detail_by_id(self, message_id):
        try:
            with safe_session() as session:
                message_details = session.query.with_entities(self.chat_id, self.message, self.sent_at, self.edited_at).filter_by(id=message_id).first()
                return message_details
        except Exception as e:
            logger.error("Error in getting message details by id: %s", e)
            return False
    
    def get_message_detail_by_ids(self, message_ids):
        try:
            with safe_session() as session:
                message_details = session.query(Messages).with_entities(Messages.message_name, Messages.is_group_message).filter(Messages.id.in_(message_ids)).all()
                return message_details
        except Exception as e:
            logger.error("Error in getting message details by ids: %s", e)
            return False
    
    def get_last_50_messages_by_room_id(self, room_id):
        try:
            with safe_session() as session:
                messages = session.query(Messages).filter_by(room_id=room_id).order_by(Messages.created_at.desc()).limit(50).all()
                return messages
        except Exception as e:
            logger.error("Error in getting last 50 messages by room id: %s", e)
            return False
