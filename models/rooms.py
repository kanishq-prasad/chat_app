from database.db import db
from datetime import datetime

class Rooms(db.Model):
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'room_code': self.room_code,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'last_activity': self.last_activity.strftime('%Y-%m-%d %H:%M:%S')
        }
