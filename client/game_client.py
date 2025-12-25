import pygame
import sys
import time
from shared.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from client.network_handler import NetworkHandler

# InputHandler (Dùng bản mới nhất gọn nhẹ)
class InputHandler:
    def get_input_data(self):
        keys = pygame.key.get_pressed()
        move_up = keys[pygame.K_UP] or keys[pygame.K_w]
        move_down = keys[pygame.K_DOWN] or keys[pygame.K_s]
        return move_up, move_down

from client.renderer import Renderer
from client.ui import UIManager

class PongClient:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Classic Pong Multiplayer")
        self.clock = pygame.time.Clock()
        
        self.ui = UIManager(self.screen)
        self.renderer = Renderer(self.screen)
        self.input_handler = InputHandler()
        
        self.state = "MENU"
        self.network = None 

    def perform_connection(self):
        """Hàm kết nối vào game"""
        self.screen.fill((0, 0, 0))
        self.ui.draw_text_centered("ĐANG TÌM TRẬN...", self.ui.font_title, (255, 255, 255), 300)
        pygame.display.flip()
        
        self.close_connection() # Đảm bảo ngắt kết nối cũ
        
        self.network = NetworkHandler()
        if self.network.connect():
            self.state = "PLAYING"
        else:
            print("❌ Không thể kết nối!")
            self.screen.fill((0, 0, 0))
            self.ui.draw_text_centered("KHÔNG TÌM THẤY SERVER!", self.ui.font_title, (255, 0, 0), 300)
            pygame.display.flip()
            time.sleep(2)
            self.state = "MENU"

    def close_connection(self):
        """Hàm tiện ích để ngắt kết nối sạch sẽ"""
        if self.network:
            print("🔌 Đóng kết nối mạng...")
            try:
                self.network.client.close()
            except:
                pass
            self.network = None

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == "MENU":
                        action = self.ui.handle_menu_click(event.pos)
                        if action == "START":
                            self.perform_connection()
                        elif action == "QUIT":
                            running = False
                    
                    elif self.state == "GAME_OVER":
                        action = self.ui.handle_game_over_click(event.pos)
                        
                        if action == "RESTART":
                            self.perform_connection()
                            
                        # --- [MỚI] XỬ LÝ NÚT VỀ MENU ---
                        elif action == "MENU":
                            print("🔙 Quay về Menu chính")
                            self.close_connection() # Ngắt kết nối với Server
                            self.state = "MENU"     # Chuyển trạng thái
                        # -------------------------------
                        
                        # Không còn nút QUIT ở đây nữa (vì đã thay bằng MENU), 
                        # nhưng cứ để logic nếu bạn muốn dùng lại sau này
                        elif action == "QUIT": 
                            running = False

            # --- LOGIC VÀ VẼ ---
            if self.state == "MENU":
                self.ui.draw_main_menu()

            elif self.state == "PLAYING":
                net_status = self.network.status
                
                if net_status == "CONNECTING":
                    self.screen.fill((0, 0, 0))
                    self.ui.draw_text_centered("ĐANG KẾT NỐI...", self.ui.font_title, (255, 255, 255), 300)

                elif net_status == "WAITING":
                    self.screen.fill((0, 0, 0))
                    self.ui.draw_text_centered("ĐANG TÌM ĐỐI THỦ...", self.ui.font_title, (255, 255, 255), 300)
                    if self.network.player_id:
                        self.ui.draw_text_centered(f"ID của bạn: {self.network.player_id}", self.ui.font_msg, (150, 150, 150), 360)

                elif net_status == "PLAYING":
                    up, down = self.input_handler.get_input_data()
                    self.network.send_input(up, down)
                    self.renderer.draw("PLAYING", self.network.current_game_state, self.network.player_id)

                elif net_status == "ENDED":
                    self.state = "GAME_OVER"
                
                elif net_status == "DISCONNECTED":
                    self.state = "MENU"

            elif self.state == "GAME_OVER":
                if self.network and self.network.current_game_state:
                    self.renderer.draw("PLAYING", self.network.current_game_state, self.network.player_id)
                self.ui.draw_game_over(self.network.winner, self.network.player_id)

            pygame.display.flip()
            self.clock.tick(FPS)

        self.close_connection()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    client = PongClient()
    client.run()