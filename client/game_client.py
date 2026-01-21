# client/game_client.py
"""
Client chính - Main game loop
"""
import time
from client.network_handler import NetworkHandler
from client.renderer import Renderer
from client.input_handler import InputHandler
from client.ui import UI
from client.sound_manager import SoundManager 
from shared.constants import *

class GameClient:
    def __init__(self):
        self.network = None # Sẽ khởi tạo mỗi khi bắt đầu game mới
        self.renderer = Renderer()
        self.input_handler = InputHandler()
        self.ui = UI()
        self.sound_manager = SoundManager()
        
        self.running = True
        self.game_started = False
        self.player_id = None
        self.winner = None 
    
    def _setup_callbacks(self):
        """Setup network callbacks"""
        self.network.set_callback(MSG_PLAYER_ID, self._on_player_id)
        self.network.set_callback(MSG_WAIT, self._on_wait)
        self.network.set_callback(MSG_READY, self._on_ready)
        self.network.set_callback(MSG_GAME_STATE, self._on_game_state)
        self.network.set_callback(MSG_GAME_OVER, self._on_game_over)
        self.network.set_callback(MSG_DISCONNECT, self._on_disconnect)
        self.network.set_callback(MSG_RESTART, self._on_restart)
    
    def _on_player_id(self, player_id):
        self.player_id = player_id
    
    def _on_wait(self):
        self.ui.set_screen("waiting")
    
    def _on_ready(self):
        print("🎮 Starting game now!")
        self.game_started = True
        self.ui.set_screen("playing")
        self.network.send_ready()
    
    def _on_game_state(self, game_state):
        """Xử lý logic âm thanh khi nhận state mới"""
        if self.network.game_state:
            old_ball = self.network.game_state.ball
            new_ball = game_state.ball
            
            # 1. Bóng đập vợt (Vận tốc X đổi chiều)
            if (old_ball.vx > 0 and new_ball.vx < 0) or (old_ball.vx < 0 and new_ball.vx > 0):
                self.sound_manager.play('paddle_hit')
            
            # 2. Bóng đập tường (Vận tốc Y đổi chiều)
            elif (old_ball.vy > 0 and new_ball.vy < 0) or (old_ball.vy < 0 and new_ball.vy > 0):
                 if new_ball.y <= 0 or new_ball.y >= SCREEN_HEIGHT - BALL_SIZE:
                    self.sound_manager.play('wall_hit')
            
            # 3. Ghi điểm
            if game_state.score1 != self.network.game_state.score1 or \
               game_state.score2 != self.network.game_state.score2:
                self.sound_manager.play('score')

    def _on_game_over(self, winner):
        """Chỉ cập nhật trạng thái, UI sẽ được vẽ ở Main Loop"""
        self.winner = winner
        self.game_started = False
        self.ui.set_screen("game_over")
        self.sound_manager.play('game_over')
    
    def _on_disconnect(self):
        self.ui.show_disconnected()
        if self.network:
            self.network.connected = False 
    
    def _on_restart(self):
        print("🎮 Game restarted!")
        self.game_started = True
        self.ui.set_screen("playing")
    
    def run(self):
        """Main game loop với cấu trúc lồng nhau để hỗ trợ quay về Menu"""
        try:
            # [VÒNG LẶP NGOÀI]: Quản lý Menu Chính
            while self.running:
                
                # 1. Hiển thị Main Menu
                choice = self.ui.show_main_menu()
                
                if choice == "exit":
                    break
                
                # Xử lý chọn chế độ (AI / Multiplayer)
                ai_mode = False
                ai_difficulty = "medium"
                
                if choice == "ai_mode":
                    difficulty = self.ui.show_ai_difficulty_menu()
                    if difficulty is None: 
                        continue # Quay lại vòng lặp ngoài (Menu chính)
                    ai_mode = True
                    ai_difficulty = difficulty
                
                # 2. Kết nối Server (Tạo network mới mỗi lần chơi)
                self.ui.show_connecting()
                self.network = NetworkHandler()
                self._setup_callbacks()
                
                if not self.network.connect(ai_mode=ai_mode, ai_difficulty=ai_difficulty):
                    self.ui.show_disconnected()
                    continue # Quay lại vòng lặp ngoài
                
                # 3. [VÒNG LẶP TRONG]: Gameplay Loop
                while self.running and self.network.is_connected():
                    self.input_handler.process_events()
                    
                    if self.input_handler.should_quit():
                        self.running = False
                        break
                    
                    # --- XỬ LÝ CÁC MÀN HÌNH ---
                    current_screen = self.ui.current_screen

                    # A. Đang chơi
                    if current_screen == "playing" and self.game_started:
                        move_up, move_down = self.input_handler.get_movement()
                        self.network.send_input(move_up, move_down)
                        
                        game_state = self.network.get_game_state()
                        if game_state:
                            self.renderer.draw_game(game_state, self.player_id)
                            self.renderer.update()
                            
                    # B. Màn hình chờ
                    elif current_screen in ["waiting", "waiting_restart"]:
                        if current_screen == "waiting":
                            self.renderer.draw_waiting()
                        else:
                            self.renderer.draw_waiting_restart()
                        self.renderer.update()
                        
                    # C. Game Over (Hiện Menu chọn)
                    elif current_screen == "game_over":
                        # Hàm này sẽ chặn (blocking) cho đến khi người dùng chọn xong
                        result = self.ui.show_game_over(self.winner, self.player_id)
                        
                        if result == "play_again":
                            self.network.send_play_again()
                            self.ui.set_screen("waiting_restart")
                            
                        elif result == "menu":
                            self.network.disconnect() # Ngắt kết nối để thoát vòng lặp trong
                            
                        elif result == "exit":
                            self.running = False
                            
                    # D. Đã ngắt kết nối
                    elif current_screen == "disconnected":
                        break # Thoát vòng lặp trong

                    time.sleep(0.001) # Giảm tải CPU
                
                # Dọn dẹp kết nối cũ khi thoát ra Menu chính
                if self.network:
                    self.network.disconnect()
                    
        except Exception as e:
            print(f"❌ Error in game loop: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        if self.network:
            self.network.disconnect()
        self.renderer.quit()
        print("✅ Cleanup complete")

def main():
    print("🎮 Classic Pong - Multiplayer Client")
    client = GameClient()
    try:
        client.run()
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        print("\n👋 Thanks for playing!")

if __name__ == "__main__":
    main()