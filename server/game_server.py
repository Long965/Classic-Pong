# server/game_server.py
import socket
import threading
import time
import json
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
        self.clients = {} 
    
    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"🎮 Server started on {self.host}:{self.port}")
            print("Waiting for players...")
            
            game_thread = threading.Thread(target=self.game_loop, daemon=True)
            game_thread.start()
            
            self.accept_connections()
            
        except Exception as e:
            print(f"❌ Error starting server: {e}")
        finally:
            self.stop()
    
    def accept_connections(self):
        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                self.clients[conn] = addr
                print(f"✅ New connection from {addr}")
                
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(conn, addr),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"❌ Error accepting connection: {e}")

    # --- ĐÃ XÓA HÀM reset_game() SAI Ở ĐÂY ---
    
    def handle_client(self, conn, addr):
        try:
            while self.running:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    break
                
                try:
                    msg_type, msg_data = Message.parse(data)
                except:
                    continue
                
                if msg_type == MSG_CONNECT:
                    self.handle_connect(conn, addr)
                
                elif msg_type == MSG_INPUT:
                    self.handle_input(conn, msg_data)
                
                elif msg_type == MSG_DISCONNECT:
                    break
        
        except Exception as e:
            print(f"❌ Error handling client {addr}: {e}")
        
        finally:
            self.disconnect_client(conn)
    
    def handle_connect(self, conn, addr):
        room_id, player_id, room_full = self.room_manager.find_or_create_room(conn, addr)
        
        try:
            conn.send(Message.player_id(player_id))
        except:
            pass
        
        if room_full:
            print(f"🎯 Room {room_id} is full! Starting game...")
            room = self.room_manager.get_room(conn)
            
            # --- GỌI HÀM RESET CỦA GAME LOGIC ---
            # Lưu ý: Hàm này nằm trong room.game_logic, KHÔNG phải trong self
            if room:
                print(f"Room {room_id}: Resetting game state...")
                room.game_logic.reset_game() 
            # ------------------------------------

            # Gửi READY
            print(f"Room {room_id}: Broadcasting READY...")
            for c in room.get_connections():
                try:
                    c.send(Message.ready())
                except:
                    pass
            
            time.sleep(0.1) 
            room.active = True 
            print(f"✅ Room {room_id} is now ACTIVE.")
            
        else:
            print(f"⏳ Player {player_id} waiting in room {room_id}...")
            try:
                conn.send(Message.wait())
            except:
                pass

    def handle_input(self, conn, data):
        player_id = self.room_manager.get_player_id(conn)
        room = self.room_manager.get_room(conn)
        if room and room.active:
            move_up = data.get('move_up', False)
            move_down = data.get('move_down', False)
            room.game_logic.set_paddle_input(player_id, move_up, move_down)
    
    def disconnect_client(self, conn):
        if conn in self.clients:
            addr = self.clients.get(conn)
            print(f"👋 Client {addr} disconnected")
            del self.clients[conn]
            
        self.room_manager.remove_player(conn)
        try:
            conn.close()
        except:
            pass
    
    def game_loop(self):
        target_fps = FPS
        frame_time = 1.0 / target_fps
        
        while self.running:
            start_time = time.time()
            active_rooms = self.room_manager.get_all_active_rooms()
            
            for room in active_rooms:
                try:
                    room.game_logic.update()
                    state_obj = room.game_logic.get_state()
                    
                    if hasattr(state_obj, 'to_dict'):
                        state_dict = state_obj.to_dict()
                    else:
                        state_dict = {
                            'ball': state_obj.ball.__dict__,
                            'paddle1': state_obj.paddle1.__dict__,
                            'paddle2': state_obj.paddle2.__dict__,
                            'score1': state_obj.score1,
                            'score2': state_obj.score2,
                            'game_over': state_obj.game_over,
                            'winner': state_obj.winner
                        }

                    state_msg = Message.create(MSG_GAME_STATE, state_dict)
                    
                    conns = room.get_connections()
                    for conn in conns:
                        try:
                            conn.send(state_msg)
                        except Exception:
                            pass
                    
                    if state_obj.game_over:
                        print(f"🏁 Game in room {room.room_id} finished.")
                        game_over_msg = Message.game_over(state_obj.winner)
                        for conn in conns:
                            try:
                                conn.send(game_over_msg)
                            except:
                                pass
                        room.active = False
                
                except Exception as e:
                    print(f"❌ Error in game loop (Room {room.room_id}): {e}")
            
            elapsed = time.time() - start_time
            sleep_time = max(0, frame_time - elapsed)
            time.sleep(sleep_time)
    
    def stop(self):
        print("\n🛑 Shutting down server...")
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

if __name__ == "__main__":
    server = GameServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()