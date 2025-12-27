# server/room_manager.py
"""
Quản lý phòng chơi và matchmaking
"""
from server.game_logic import GameLogic
from server.ai_player import AIPlayer

class Room:
    def __init__(self, room_id, ai_mode=False, ai_difficulty="medium"):
        self.room_id = room_id
        self.player1 = None
        self.player2 = None
        self.game_logic = GameLogic()
        self.ready_count = 0
        self.active = False
        self.play_again_count = 0
        
        # AI Mode
        self.ai_mode = ai_mode
        self.ai_player = None
        if ai_mode:
            self.ai_player = AIPlayer(difficulty=ai_difficulty)
            print(f"🤖 Room {room_id} created with AI ({ai_difficulty})")
    
    def add_player(self, conn, addr):
        """Thêm player vào phòng"""
        if self.player1 is None:
            self.player1 = {'conn': conn, 'addr': addr, 'ready': False}
            
            # Nếu AI mode, tự động thêm AI làm player 2
            if self.ai_mode:
                self.player2 = {'conn': None, 'addr': 'AI', 'ready': True}
                self.ready_count = 1  # AI luôn ready
                print(f"🤖 AI joined room {self.room_id} as Player 2")
            
            return 1
        elif self.player2 is None and not self.ai_mode:
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
        if self.ai_mode:
            # AI mode chỉ cần 1 player
            return self.player1 is not None
        return self.player1 is not None and self.player2 is not None
    
    def is_empty(self):
        """Kiểm tra phòng có rỗng không"""
        return self.player1 is None and self.player2 is None
    
    def set_ready(self, player_id):
        """Set player ready"""
        if player_id == 1 and self.player1:
            self.player1['ready'] = True
            self.ready_count += 1
        elif player_id == 2 and self.player2 and not self.ai_mode:
            self.player2['ready'] = True
            self.ready_count += 1
        
        # Nếu cả 2 ready thì start game
        # (AI mode: chỉ cần player 1 ready vì AI luôn ready)
        required_ready = 1 if self.ai_mode else 2
        if self.ready_count >= required_ready:
            self.active = True
    
    def restart_game(self):
        """Restart game cho chơi lại"""
        self.game_logic = GameLogic()  # Tạo game logic mới
        self.game_logic.reset_ball()
        self.play_again_count = 0
        self.active = True
        print(f"♻️  Room {self.room_id} restarted!")
    
    def set_play_again(self, player_id):
        """Player muốn chơi lại"""
        self.play_again_count += 1
        print(f"🔄 Player {player_id} wants to play again ({self.play_again_count}/2)")
        
        # Nếu cả 2 đều muốn chơi lại
        if self.play_again_count >= 2:
            self.restart_game()
            return True
        return False
    
    def get_connections(self):
        """Lấy tất cả connections"""
        conns = []
        if self.player1 and self.player1['conn']:
            conns.append(self.player1['conn'])
        if self.player2 and self.player2['conn'] and not self.ai_mode:
            conns.append(self.player2['conn'])
        return conns
    
    def update_ai(self):
        """Update AI movement"""
        if self.ai_mode and self.ai_player and self.active:
            move_up, move_down = self.ai_player.calculate_move(self.game_logic.get_state())
            self.game_logic.set_paddle_input(2, move_up, move_down)


class RoomManager:
    def __init__(self):
        self.rooms = {}
        self.next_room_id = 1
        self.player_room_map = {}  # {conn: (room_id, player_id)}
    
    def find_or_create_room(self, conn, addr, ai_mode=False, ai_difficulty="medium"):
        """Tìm phòng available hoặc tạo phòng mới"""
        # Nếu AI mode, luôn tạo phòng mới
        if ai_mode:
            room_id = self.next_room_id
            self.next_room_id += 1
            room = Room(room_id, ai_mode=True, ai_difficulty=ai_difficulty)
            player_id = room.add_player(conn, addr)
            self.rooms[room_id] = room
            self.player_room_map[conn] = (room_id, player_id)
            return room_id, player_id, room.is_full()
        
        # Multiplayer mode: tìm phòng chưa đầy
        for room_id, room in self.rooms.items():
            if not room.ai_mode and not room.is_full():
                player_id = room.add_player(conn, addr)
                if player_id:
                    self.player_room_map[conn] = (room_id, player_id)
                    return room_id, player_id, room.is_full()
        
        # Tạo phòng multiplayer mới
        room_id = self.next_room_id
        self.next_room_id += 1
        room = Room(room_id, ai_mode=False)
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