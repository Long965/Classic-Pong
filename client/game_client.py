import pygame
import sys
import os

# Thêm thư mục gốc vào path để import được shared
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.network_handler import NetworkHandler
from client.renderer import Renderer
from client.input_handler import InputHandler
from shared.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

class PongClient:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Classic Pong Multiplayer")
        
        self.network = NetworkHandler()
        self.renderer = Renderer(self.screen)
        self.input_handler = InputHandler()
        self.clock = pygame.time.Clock()

    def run(self):
        # 1. Kết nối tới server
        if not self.network.connect():
            print("Không thể kết nối tới server!")
            return

        running = True
        while running:
            # 2. Xử lý Input từ người dùng
            running = self.input_handler.update()
            
            # 3. Gửi Input lên Server (chỉ gửi khi đang chơi)
            if self.network.status == "PLAYING":
                up, down = self.input_handler.get_input_data()
                self.network.send_input(up, down)

            # 4. Vẽ màn hình dựa trên dữ liệu mạng mới nhất
            self.renderer.draw(
                self.network.status, 
                self.network.current_game_state,
                self.network.player_id
            )

            # 5. Duy trì FPS
            self.clock.tick(FPS)

        pygame.quit()

if __name__ == "__main__":
    client = PongClient()
    client.run()