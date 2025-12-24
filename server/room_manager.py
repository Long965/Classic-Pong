# server/room_manager.py
"""
Quản lý phòng chơi và matchmaking
"""
from server.game_logic import GameLogic

class Room:
    def __init__(self, room_id):
        self.room_id = room_id
        self.player1 = None
        self.player2 = None
        self.game_logic = GameLogic()
        self.ready_count = 0
        self.active = False
    
    def add_player(self, conn, addr):
        """Thêm player vào phòng"""
        if self.player1 is None:
            self.player1 = {'conn': conn, 'addr': addr, 'ready': False}
            return 1
        elif self.player2 is None:
            self.player2 = {'conn': conn, 'addr': addr, 'ready': False}
            return 2
        return None
    
    def remove_player(self, player_id):
        """Xóa player khỏi phòng"""
        if player_id == 1:
            self.player1 = None
        elif player_id == 2:
            self.player2 = None
        self.ready_count = 0
        self.active = False
    
    def is_full(self):
        """Kiểm tra phòng đã đầy chưa"""
        return self.player1 is not None and self.player2 is not None
    
    def is_empty(self):
        """Kiểm tra phòng có rỗng không"""
        return self.player1 is None and self.player2 is None
    
    def set_ready(self, player_id):
        """Set player ready"""
        if player_id == 1 and self.player1:
            self.player1['ready'] = True
            self.ready_count += 1
        elif player_id == 2 and self.player2:
            self.player2['ready'] = True
            self.ready_count += 1
        
        # Nếu cả 2 ready thì start game
        if self.ready_count == 2:
            self.active = True
    
    def get_connections(self):
        """Lấy tất cả connections"""
        conns = []
        if self.player1:
            conns.append(self.player1['conn'])
        if self.player2:
            conns.append(self.player2['conn'])
        return conns


class RoomManager:
    def __init__(self):
        self.rooms = {}
        self.next_room_id = 1
        self.player_room_map = {}  # {conn: (room_id, player_id)}
    
    def find_or_create_room(self, conn, addr):
        """Tìm phòng available hoặc tạo phòng mới"""
        # Tìm phòng chưa đầy
        for room_id, room in self.rooms.items():
            if not room.is_full():
                player_id = room.add_player(conn, addr)
                if player_id:
                    self.player_room_map[conn] = (room_id, player_id)
                    return room_id, player_id, room.is_full()
        
        # Tạo phòng mới
        room_id = self.next_room_id
        self.next_room_id += 1
        room = Room(room_id)
        player_id = room.add_player(conn, addr)
        self.rooms[room_id] = room
        self.player_room_map[conn] = (room_id, player_id)
        
        return room_id, player_id, False
    
    def get_room(self, conn):
        """Lấy room của connection"""
        if conn in self.player_room_map:
            room_id, _ = self.player_room_map[conn]
            return self.rooms.get(room_id)
        return None
    
    def get_player_id(self, conn):
        """Lấy player ID của connection"""
        if conn in self.player_room_map:
            _, player_id = self.player_room_map[conn]
            return player_id
        return None
    
    def remove_player(self, conn):
        """Xóa player khỏi phòng"""
        if conn in self.player_room_map:
            room_id, player_id = self.player_room_map[conn]
            room = self.rooms.get(room_id)
            
            if room:
                room.remove_player(player_id)
                
                # Xóa phòng nếu rỗng
                if room.is_empty():
                    del self.rooms[room_id]
            
            del self.player_room_map[conn]
    
    def get_all_active_rooms(self):
        """Lấy tất cả phòng đang active"""
        return [room for room in self.rooms.values() if room.active]