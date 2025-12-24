# server/game_server.py
"""
Server chính quản lý kết nối và game loop
"""
import socket
import threading
import time
from shared.constants import *
from shared.protocol import Message
from server.room_manager import RoomManager

class GameServer:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.server_socket = None
        self.room_manager = RoomManager()
        self.running = False
        self.clients = {}  # {conn: addr}
    
    def start(self):
        """Khởi động server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"🎮 Server started on {self.host}:{self.port}")
            print("Waiting for players...")
            
            # Start game loop thread
            game_thread = threading.Thread(target=self.game_loop, daemon=True)
            game_thread.start()
            
            # Accept connections
            self.accept_connections()
            
        except Exception as e:
            print(f"❌ Error starting server: {e}")
        finally:
            self.stop()
    
    def accept_connections(self):
        """Accept client connections"""
        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                self.clients[conn] = addr
                print(f"✅ New connection from {addr}")
                
                # Handle client in new thread
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(conn, addr),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"❌ Error accepting connection: {e}")
    
    def handle_client(self, conn, addr):
        """Xử lý messages từ client"""
        try:
            while self.running:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    break
                
                msg_type, msg_data = Message.parse(data)
                
                if msg_type == MSG_CONNECT:
                    self.handle_connect(conn, addr)
                
                elif msg_type == MSG_READY:
                    self.handle_ready(conn)
                
                elif msg_type == MSG_INPUT:
                    self.handle_input(conn, msg_data)
                
                elif msg_type == MSG_DISCONNECT:
                    break
        
        except Exception as e:
            print(f"❌ Error handling client {addr}: {e}")
        
        finally:
            self.disconnect_client(conn)
    
    def handle_connect(self, conn, addr):
        """Xử lý khi client connect"""
        room_id, player_id, room_full = self.room_manager.find_or_create_room(conn, addr)
        
        # Gửi player ID
        conn.send(Message.player_id(player_id))
        
        if room_full:
            print(f"🎯 Room {room_id} is full! Starting game...")
            room = self.room_manager.get_room(conn)
            for c in room.get_connections():
                try:
                    c.send(Message.ready())
                except:
                    pass
        else:
            print(f"⏳ Player {player_id} waiting in room {room_id}...")
            conn.send(Message.wait())
    
    def handle_ready(self, conn):
        """Xử lý khi player ready"""
        player_id = self.room_manager.get_player_id(conn)
        room = self.room_manager.get_room(conn)
        
        if room:
            room.set_ready(player_id)
            print(f"✓ Player {player_id} ready in room {room.room_id}")
    
    def handle_input(self, conn, data):
        """Xử lý input từ player"""
        player_id = self.room_manager.get_player_id(conn)
        room = self.room_manager.get_room(conn)
        
        if room and room.active:
            move_up = data.get('move_up', False)
            move_down = data.get('move_down', False)
            room.game_logic.set_paddle_input(player_id, move_up, move_down)
    
    def disconnect_client(self, conn):
        """Xử lý disconnect"""
        addr = self.clients.get(conn)
        print(f"👋 Client {addr} disconnected")
        
        # Remove from room
        room = self.room_manager.get_room(conn)
        if room:
            # Notify other player
            for c in room.get_connections():
                if c != conn:
                    try:
                        c.send(Message.disconnect())
                    except:
                        pass
        
        self.room_manager.remove_player(conn)
        
        if conn in self.clients:
            del self.clients[conn]
        
        try:
            conn.close()
        except:
            pass
    
    def game_loop(self):
        """Main game loop - chạy ở 60 FPS"""
        target_fps = FPS
        frame_time = 1.0 / target_fps
        
        while self.running:
            start_time = time.time()
            
            # Update tất cả active rooms
            active_rooms = self.room_manager.get_all_active_rooms()
            
            for room in active_rooms:
                try:
                    # Update game logic
                    room.game_logic.update()
                    
                    # Broadcast game state
                    state = room.game_logic.get_state()
                    state_msg = Message.game_state(state)
                    
                    for conn in room.get_connections():
                        try:
                            conn.send(state_msg)
                        except:
                            pass
                    
                    # Check game over
                    if state.game_over:
                        game_over_msg = Message.game_over(state.winner)
                        for conn in room.get_connections():
                            try:
                                conn.send(game_over_msg)
                            except:
                                pass
                        room.active = False
                
                except Exception as e:
                    print(f"❌ Error in game loop for room {room.room_id}: {e}")
            
            # Sleep để duy trì FPS
            elapsed = time.time() - start_time
            sleep_time = max(0, frame_time - elapsed)
            time.sleep(sleep_time)
    
    def stop(self):
        """Dừng server"""
        print("\n🛑 Shutting down server...")
        self.running = False
        
        # Close all client connections
        for conn in list(self.clients.keys()):
            try:
                conn.close()
            except:
                pass
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print("✅ Server stopped")


if __name__ == "__main__":
    server = GameServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n⚠️ Server interrupted by user")
        server.stop()