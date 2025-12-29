# client/network_handler.py
"""
Xử lý network communication
"""
import socket
import threading
from shared.constants import *
from shared.protocol import Message
from shared.models import GameState

class NetworkHandler:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.player_id = None
        self.game_state = None
        self.waiting = False
        self.game_over = False
        self.winner = None
        self.receive_thread = None
        self.callbacks = {
            MSG_PLAYER_ID: None,
            MSG_WAIT: None,
            MSG_READY: None,
            MSG_GAME_STATE: None,
            MSG_GAME_OVER: None,
            MSG_DISCONNECT: None,
            MSG_RESTART: None
        }
    
    def connect(self, ai_mode=False, ai_difficulty="medium"):
        """Kết nối đến server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            
            # Gửi connect message hoặc AI mode message
            if ai_mode:
                self.socket.send(Message.ai_mode(ai_difficulty))
                print(f"🤖 Requesting AI game ({ai_difficulty})...")
            else:
                self.socket.send(Message.connect())
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            
            print(f"✅ Connected to server {self.host}:{self.port}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Ngắt kết nối"""
        if self.connected and self.socket:
            try:
                self.socket.send(Message.disconnect())
            except:
                pass
            
            try:
                self.socket.close()
            except:
                pass
            
            self.connected = False
            print("👋 Disconnected from server")
    
    def send_ready(self):
        """Gửi ready signal"""
        if self.connected:
            try:
                self.socket.send(Message.ready())
            except Exception as e:
                print(f"❌ Failed to send ready: {e}")
    
    def send_input(self, move_up, move_down):
        """Gửi input đến server"""
        if self.connected:
            try:
                self.socket.send(Message.input_data(move_up, move_down))
            except Exception as e:
                print(f"❌ Failed to send input: {e}")
                self.connected = False
    
    def send_play_again(self):
        """Gửi yêu cầu chơi lại"""
        if self.connected:
            try:
                self.socket.send(Message.play_again())
                print("🔄 Requested to play again...")
            except Exception as e:
                print(f"❌ Failed to send play again: {e}")
                self.connected = False
    
    def _receive_loop(self):
        """Loop nhận data từ server"""
        while self.connected:
            try:
                data = self.socket.recv(BUFFER_SIZE)
                if not data:
                    print("⚠️ Server closed connection")
                    self.connected = False
                    break
                
                msg_type, msg_data = Message.parse(data)
                self._handle_message(msg_type, msg_data)
                
            except Exception as e:
                if self.connected:
                    print(f"❌ Error receiving data: {e}")
                    self.connected = False
                break
    
    def _handle_message(self, msg_type, msg_data):
        """Xử lý message từ server"""
        if msg_type == MSG_PLAYER_ID:
            self.player_id = msg_data.get('id')
            print(f"🎮 You are Player {self.player_id}")
            if self.callbacks[MSG_PLAYER_ID]:
                self.callbacks[MSG_PLAYER_ID](self.player_id)
        
        elif msg_type == MSG_WAIT:
            self.waiting = True
            print("⏳ Waiting for another player...")
            if self.callbacks[MSG_WAIT]:
                self.callbacks[MSG_WAIT]()
        
        elif msg_type == MSG_READY:
            self.waiting = False
            print("🎯 Game starting!")
            if self.callbacks[MSG_READY]:
                self.callbacks[MSG_READY]()
        
        elif msg_type == MSG_GAME_STATE:
            self.game_state = GameState.from_dict(msg_data)
            if self.callbacks[MSG_GAME_STATE]:
                self.callbacks[MSG_GAME_STATE](self.game_state)
        
        elif msg_type == MSG_GAME_OVER:
            self.game_over = True
            self.winner = msg_data.get('winner')
            print(f"🏆 Game Over! Player {self.winner} wins!")
            if self.callbacks[MSG_GAME_OVER]:
                self.callbacks[MSG_GAME_OVER](self.winner)
        
        elif msg_type == MSG_DISCONNECT:
            print("⚠️ Other player disconnected")
            self.connected = False
            if self.callbacks[MSG_DISCONNECT]:
                self.callbacks[MSG_DISCONNECT]()
        
        elif msg_type == MSG_RESTART:
            print("♻️  Game restarting...")
            self.game_over = False
            self.winner = None
            if self.callbacks[MSG_RESTART]:
                self.callbacks[MSG_RESTART]()
    
    def set_callback(self, msg_type, callback):
        """Set callback cho message type"""
        if msg_type in self.callbacks:
            self.callbacks[msg_type] = callback
    
    def is_connected(self):
        """Check connection status"""
        return self.connected
    
    def get_game_state(self):
        """Lấy game state hiện tại"""
        return self.game_state
    
    def get_player_id(self):
        """Lấy player ID"""
        return self.player_id