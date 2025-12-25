import pygame
from shared.constants import *

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Consolas", FONT_SIZE)
        self.small_font = pygame.font.SysFont("Consolas", SMALL_FONT_SIZE)

    def draw(self, status, state, player_id):
        self.screen.fill((0, 0, 0)) # Màu đen (BLACK)
        
        if status == "WAITING":
            self._draw_text("WAITING FOR PLAYER 2...", 400, 300)
        
        elif status == "PLAYING":
            if state is None:
                # Nếu ở trạng thái PLAYING nhưng chưa có dữ liệu, hiện thông báo chờ
                self._draw_text("LOADING GAME STATE...", 400, 300)
                pygame.display.flip()
                return

            # VẼ CÁC ĐỐI TƯỢNG (Dựa trên models.py)
            # Vẽ bóng
            ball = state.get('ball', {})
            pygame.draw.rect(self.screen, (255, 255, 255), 
                            (ball.get('x', 0), ball.get('y', 0), 15, 15))
            
            # Vẽ Paddle 1 và 2
            p1 = state.get('paddle1', {})
            p2 = state.get('paddle2', {})
            pygame.draw.rect(self.screen, (255, 255, 255), (p1.get('x', 0), p1.get('y', 0), 15, 100))
            pygame.draw.rect(self.screen, (255, 255, 255), (p2.get('x', 0), p2.get('y', 0), 15, 100))

            # Vẽ tỉ số
            self._draw_text(f"{state.get('score1', 0)} - {state.get('score2', 0)}", 400, 50)

        pygame.display.flip()

    def _draw_text(self, text, x, y, font=None):
        if font is None: font = self.font
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)