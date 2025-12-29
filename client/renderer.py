# client/renderer.py
"""
Vẽ graphics với Pygame
"""
import pygame
import random # <--- THÊM DÒNG NÀY
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

        # --- BỔ SUNG ĐỂ THEO DÕI BÓNG ---
        self.ball_color = WHITE  # Màu ban đầu
        self.last_ball_x = width // 2 # Vị trí X của bóng ở frame trước
        # Hướng di chuyển frame trước (1 là phải, -1 là trái, 0 là đứng yên)
        self.last_dx_sign = 0
    
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
        self._draw_paddle(game_state.paddle2, player_id == 2 or player_id == 1)  # Highlight both if vs AI
        
        # Draw ball
        self._draw_ball(game_state.ball)
        
        # Draw scores
        self._draw_scores(game_state.score1, game_state.score2)
        
        # Draw player indicator
        if player_id:
            self._draw_player_indicator(player_id)
        
        # Draw AI indicator nếu là AI mode
        if player_id == 1:  # Player 1 vs AI
            self._draw_ai_indicator()
    
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
    
    def _get_random_bright_color(self):
        """Tạo một màu RGB sáng ngẫu nhiên"""
        # Đảm bảo màu không quá tối bằng cách random từ 100-255
        r = random.randint(100, 255)
        g = random.randint(100, 255)
        b = random.randint(100, 255)
        return (r, g, b)

    def _draw_ball(self, ball):
        """Vẽ bóng to hơn, hình tròn và đổi màu khi chạm thanh"""

        # --- 1. Logic đổi màu (Giữ nguyên như trước) ---
        current_dx = ball.x - self.last_ball_x
        current_sign = 0
        if current_dx > 0: current_sign = 1
        elif current_dx < 0: current_sign = -1

        if current_sign != 0 and current_sign != self.last_dx_sign:
            if self.last_dx_sign != 0:
                self.ball_color = self._get_random_bright_color()
            self.last_dx_sign = current_sign

        self.last_ball_x = ball.x

        # --- 2. Vẽ bóng TO HƠN ---
        
        # Bước A: Tính tâm của bóng dựa trên hitbox thật (để bóng không bị lệch)
        # ball.size là kích thước thật từ server gửi về
        real_center_x = int(ball.x + ball.size / 2)
        real_center_y = int(ball.y + ball.size / 2)

        # Bước B: Tự quy định bán kính vẽ (Visual Radius)
        # Bạn có thể nhân lên (ví dụ * 1.5) hoặc gán số cố định
        # Ví dụ: ball.size mặc định thường là 10, ta vẽ radius = 10 (đường kính 20 -> to gấp đôi)
        visual_radius = int(ball.size * 0.8) # <--- CHỈNH SỐ NÀY ĐỂ BÓNG TO/NHỎ
        # Hoặc gán cứng: visual_radius = 15 

        pygame.draw.circle(
            self.screen,
            self.ball_color,
            (real_center_x, real_center_y),
            visual_radius
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
    
    def _draw_ai_indicator(self):
        """Vẽ indicator cho AI"""
        text = "🤖 AI Opponent"
        indicator = self.font_small.render(text, True, (255, 100, 100))
        rect = indicator.get_rect()
        rect.bottomleft = (10, self.height - 10)
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
    
    def draw_waiting_restart(self):
        """Vẽ màn hình chờ player khác chơi lại"""
        self.clear()
        
        text = "Waiting for other player..."
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

    def draw_game_over(self, winner, player_id, selected_option=0):
        """Vẽ màn hình game over với menu lựa chọn"""
        self.clear()
        
        # 1. Vẽ kết quả (Thắng/Thua)
        if winner == player_id:
            result_text = TEXT_WIN
            color = (100, 255, 100)
        else:
            result_text = TEXT_LOSE
            color = (255, 100, 100)
        
        result = self.font_large.render(result_text, True, color)
        rect = result.get_rect()
        rect.center = (self.width // 2, self.height // 2 - 100)
        self.screen.blit(result, rect)
        
        # Vẽ tên người thắng
        winner_text = TEXT_WINNER_ANNO.format(winner)
        winner_render = self.font_small.render(winner_text, True, WHITE)
        winner_rect = winner_render.get_rect()
        winner_rect.center = (self.width // 2, self.height // 2 - 50)
        self.screen.blit(winner_render, winner_rect)
        
        # 2. Vẽ Menu Lựa Chọn (Chơi Lại / Về Menu)
        options = [TEXT_PLAY_AGAIN, TEXT_MAIN_MENU]
        start_y = self.height // 2 + 30
        
        for i, option in enumerate(options):
            # Đổi màu nếu đang được chọn
            color = (100, 200, 255) if i == selected_option else GRAY
            
            text = self.font_small.render(option, True, color)
            rect = text.get_rect()
            rect.center = (self.width // 2, start_y + i * 40)
            
            # Vẽ mũi tên chỉ vào dòng đang chọn
            if i == selected_option:
                arrow = self.font_small.render(">", True, (100, 200, 255))
                arrow_rect = arrow.get_rect()
                arrow_rect.center = (self.width // 2 - 120, start_y + i * 40)
                self.screen.blit(arrow, arrow_rect)
                
            self.screen.blit(text, rect)
            
        # 3. Vẽ hướng dẫn
        hint = self.font_small.render(TEXT_GAME_OVER_HINT, True, (80, 80, 80))
        hint_rect = hint.get_rect()
        hint_rect.center = (self.width // 2, self.height - 30)
        self.screen.blit(hint, hint_rect)
    
    def draw_connecting(self):
        """Vẽ màn hình đang kết nối"""
        self.clear()
        
        text = "Connecting to server..."
        conn_text = self.font_small.render(text, True, WHITE)
        rect = conn_text.get_rect()
        rect.center = (self.width // 2, self.height // 2)
        self.screen.blit(conn_text, rect)
    
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