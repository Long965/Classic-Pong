# client/renderer.py
"""
Vẽ graphics với Pygame
"""
import pygame
from shared.constants import *

class Renderer:
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Classic Pong - Multiplayer")
        
        # Fonts
        self.font_large = pygame.font.Font(None, FONT_SIZE)
        self.font_small = pygame.font.Font(None, SMALL_FONT_SIZE)
        
        # Clock for FPS
        self.clock = pygame.time.Clock()
    
    def clear(self):
        """Xóa màn hình"""
        self.screen.fill(BLACK)
    
    def draw_game(self, game_state, player_id=None):
        """Vẽ game state"""
        if not game_state:
            return
        
        self.clear()
        
        # Draw net
        self._draw_net()
        
        # Draw paddles
        self._draw_paddle(game_state.paddle1, player_id == 1)
        self._draw_paddle(game_state.paddle2, player_id == 2)
        
        # Draw ball
        self._draw_ball(game_state.ball)
        
        # Draw scores
        self._draw_scores(game_state.score1, game_state.score2)
        
        # Draw player indicator
        if player_id:
            self._draw_player_indicator(player_id)
    
    def _draw_net(self):
        """Vẽ lưới giữa màn hình"""
        net_height = 15
        net_gap = 10
        x = self.width // 2 - NET_WIDTH // 2
        
        for y in range(0, self.height, net_height + net_gap):
            pygame.draw.rect(self.screen, GRAY, (x, y, NET_WIDTH, net_height))
    
    def _draw_paddle(self, paddle, is_current_player=False):
        """Vẽ paddle"""
        color = WHITE
        if is_current_player:
            color = (100, 200, 255)  # Màu xanh dương cho paddle của mình
        
        pygame.draw.rect(
            self.screen,
            color,
            (paddle.x, paddle.y, paddle.width, paddle.height)
        )
    
    def _draw_ball(self, ball):
        """Vẽ bóng"""
        pygame.draw.rect(
            self.screen,
            WHITE,
            (ball.x, ball.y, ball.size, ball.size)
        )
    
    def _draw_scores(self, score1, score2):
        """Vẽ điểm số"""
        # Score Player 1 (left)
        score1_text = self.font_large.render(str(score1), True, WHITE)
        score1_rect = score1_text.get_rect()
        score1_rect.center = (self.width // 4, 50)
        self.screen.blit(score1_text, score1_rect)
        
        # Score Player 2 (right)
        score2_text = self.font_large.render(str(score2), True, WHITE)
        score2_rect = score2_text.get_rect()
        score2_rect.center = (3 * self.width // 4, 50)
        self.screen.blit(score2_text, score2_rect)
    
    def _draw_player_indicator(self, player_id):
        """Vẽ indicator cho player"""
        text = f"You: Player {player_id}"
        indicator = self.font_small.render(text, True, (100, 200, 255))
        rect = indicator.get_rect()
        rect.bottomright = (self.width - 10, self.height - 10)
        self.screen.blit(indicator, rect)
    
    def draw_menu(self, title, options, selected=0):
        """Vẽ menu"""
        self.clear()
        
        # Title
        title_text = self.font_large.render(title, True, WHITE)
        title_rect = title_text.get_rect()
        title_rect.center = (self.width // 2, self.height // 4)
        self.screen.blit(title_text, title_rect)
        
        # Instructions
        hint_text = self.font_small.render("Use W/S or Arrow keys to navigate, Enter to select", True, GRAY)
        hint_rect = hint_text.get_rect()
        hint_rect.center = (self.width // 2, self.height // 4 + 60)
        self.screen.blit(hint_text, hint_rect)
        
        # Options
        y_start = self.height // 2
        for i, option in enumerate(options):
            color = (100, 200, 255) if i == selected else WHITE
            
            # Draw selector arrow
            if i == selected:
                arrow = self.font_small.render(">", True, (100, 200, 255))
                arrow_rect = arrow.get_rect()
                arrow_rect.center = (self.width // 2 - 150, y_start + i * 50)
                self.screen.blit(arrow, arrow_rect)
            
            option_text = self.font_small.render(option, True, color)
            option_rect = option_text.get_rect()
            option_rect.center = (self.width // 2, y_start + i * 50)
            self.screen.blit(option_text, option_rect)
    
    def draw_waiting(self):
        """Vẽ màn hình chờ"""
        self.clear()
        
        text = "Waiting for another player..."
        waiting_text = self.font_small.render(text, True, WHITE)
        rect = waiting_text.get_rect()
        rect.center = (self.width // 2, self.height // 2)
        self.screen.blit(waiting_text, rect)
        
        # Animation dots
        dots = "." * (pygame.time.get_ticks() // 500 % 4)
        dots_text = self.font_small.render(dots, True, WHITE)
        dots_rect = dots_text.get_rect()
        dots_rect.center = (self.width // 2, self.height // 2 + 40)
        self.screen.blit(dots_text, dots_rect)
    
    def draw_game_over(self, winner, player_id):
        """Vẽ màn hình game over"""
        self.clear()
        
        # Result
        if winner == player_id:
            result_text = "YOU WIN!"
            color = (100, 255, 100)
        else:
            result_text = "YOU LOSE!"
            color = (255, 100, 100)
        
        result = self.font_large.render(result_text, True, color)
        rect = result.get_rect()
        rect.center = (self.width // 2, self.height // 2 - 50)
        self.screen.blit(result, rect)
        
        # Instructions
        instruction = self.font_small.render("Press ESC to exit", True, WHITE)
        inst_rect = instruction.get_rect()
        inst_rect.center = (self.width // 2, self.height // 2 + 50)
        self.screen.blit(instruction, inst_rect)
    
    def draw_disconnected(self):
        """Vẽ màn hình disconnect"""
        self.clear()
        
        text = "Disconnected from server"
        disc_text = self.font_small.render(text, True, (255, 100, 100))
        rect = disc_text.get_rect()
        rect.center = (self.width // 2, self.height // 2)
        self.screen.blit(disc_text, rect)
        
        instruction = self.font_small.render("Press ESC to exit", True, WHITE)
        inst_rect = instruction.get_rect()
        inst_rect.center = (self.width // 2, self.height // 2 + 40)
        self.screen.blit(instruction, inst_rect)
    
    def draw_connecting(self):
        """Vẽ màn hình đang kết nối"""
        self.clear()
        
        text = "Connecting to server..."
        conn_text = self.font_small.render(text, True, WHITE)
        rect = conn_text.get_rect()
        rect.center = (self.width // 2, self.height // 2)
        self.screen.blit(conn_text, rect)
    
    def update(self):
        """Update display"""
        pygame.display.flip()
        self.clock.tick(FPS)
    
    def get_fps(self):
        """Lấy FPS hiện tại"""
        return self.clock.get_fps()
    
    def quit(self):
        """Quit pygame"""
        pygame.quit()