import pygame
from shared.constants import SCREEN_WIDTH, SCREEN_HEIGHT

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
HOVER_COLOR = (50, 200, 50)

class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont("Arial", 50, bold=True)
        self.font_btn = pygame.font.SysFont("Arial", 25, bold=True)
        self.font_msg = pygame.font.SysFont("Arial", 20)

        center_x = SCREEN_WIDTH // 2
        
        # Nút ở Menu chính
        self.btn_start = pygame.Rect(center_x - 100, 300, 200, 50)
        self.btn_quit_menu = pygame.Rect(center_x - 100, 370, 200, 50)
        
        # Nút ở màn hình Game Over
        self.btn_restart = pygame.Rect(center_x - 100, 300, 200, 50)
        # Đổi tên biến cho rõ ràng
        self.btn_back_menu = pygame.Rect(center_x - 100, 370, 200, 50) 

    def draw_text_centered(self, text, font, color, y_pos):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
        self.screen.blit(surface, rect)

    def draw_button(self, rect, text, hover=False):
        color = HOVER_COLOR if hover else GRAY
        border_color = WHITE if hover else (200, 200, 200)
        
        pygame.draw.rect(self.screen, color, rect, border_radius=12)
        pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=12)
        
        text_surf = self.font_btn.render(text, True, WHITE)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def draw_main_menu(self):
        self.screen.fill(BLACK)
        self.draw_text_centered("CLASSIC PONG ONLINE", self.font_title, WHITE, 150)
        self.draw_text_centered("Kết nối bạn bè - Tranh tài đỉnh cao", self.font_msg, (200, 200, 200), 210)
        
        mouse_pos = pygame.mouse.get_pos()
        self.draw_button(self.btn_start, "TÌM TRẬN ĐẤU", self.btn_start.collidepoint(mouse_pos))
        self.draw_button(self.btn_quit_menu, "THOÁT GAME", self.btn_quit_menu.collidepoint(mouse_pos))

    def draw_game_over(self, winner_id, my_id):
        # Lớp phủ mờ
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0,0))

        if winner_id == my_id:
            msg = "🏆 CHIẾN THẮNG! 🏆"
            color = GREEN
        else:
            msg = "😢 THẤT BẠI... 😢"
            color = RED
            
        self.draw_text_centered(msg, self.font_title, color, 150)
        
        mouse_pos = pygame.mouse.get_pos()
        # Nút Chơi Lại
        self.draw_button(self.btn_restart, "CHƠI LẠI", self.btn_restart.collidepoint(mouse_pos))
        
        # [SỬA] Nút Về Menu (Thay vì Thoát Game)
        self.draw_button(self.btn_back_menu, "VỀ MENU CHÍNH", self.btn_back_menu.collidepoint(mouse_pos))

    def handle_menu_click(self, pos):
        if self.btn_start.collidepoint(pos):
            return "START"
        if self.btn_quit_menu.collidepoint(pos):
            return "QUIT"
        return None

    def handle_game_over_click(self, pos):
        if self.btn_restart.collidepoint(pos):
            return "RESTART"
        
        # [SỬA] Trả về action MENU
        if self.btn_back_menu.collidepoint(pos):
            return "MENU" 
            
        return None