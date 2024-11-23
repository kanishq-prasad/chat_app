class RoomManager:
    def __init__(self):
        self.rooms = {}
        self.room_messages = {}
    
    def create_room(self, room_code):
        if room_code not in self.rooms:
            self.rooms[room_code] = set()
            self.room_messages[room_code] = []
            return True
        return False
    
    def join_room(self, room_code, username):
        if room_code not in self.rooms:
            self.create_room(room_code)
        self.rooms[room_code].add(username)
        return True
    
    def leave_room(self, room_code, username):
        if room_code in self.rooms:
            self.rooms[room_code].discard(username)
            if len(self.rooms[room_code]) == 0:
                del self.rooms[room_code]
                del self.room_messages[room_code]
    
    def get_active_users(self, room_code):
        return self.rooms.get(room_code, set())