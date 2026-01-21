"""
Logic game: vật lý, va chạm, tính điểm
Fix lỗi: 'dict' object has no attribute 'ball'
"""
import random
from shared.models import GameState
from shared.constants import *

# Danh sách màu rực rỡ
BRIGHT_COLORS = [
    "#FF0000", "#00FF00", "#0000FF", "#FFFF00", 
    "#00FFFF", "#FF00FF", "#FFA500", "#FFFFFF"
]

class GameLogic:
    def __init__(self):
        self.state = GameState()
        self.ball_color = "#FFFFFF" # Mặc định màu trắng
        self.reset_ball()
    
    def reset_ball(self, direction=None):
        """Reset bóng về giữa màn hình"""
        self.state.ball.x = SCREEN_WIDTH // 2
        self.state.ball.y = SCREEN_HEIGHT // 2
        self.ball_color = "#FFFFFF" # Reset màu
        
        # Random hướng bay
        if direction is None:
            direction = random.choice([-1, 1])
        
        self.state.ball.vx = BALL_SPEED_X * direction
        self.state.ball.vy = random.uniform(-BALL_SPEED_Y, BALL_SPEED_Y)

    def reset_game(self):
        """Reset toàn bộ trạng thái"""
        self.state.score1 = 0
        self.state.score2 = 0
        self.state.game_over = False
        self.state.winner = None
        
        self.state.paddle1.y = (SCREEN_HEIGHT - PADDLE_HEIGHT) // 2
        self.state.paddle2.y = (SCREEN_HEIGHT - PADDLE_HEIGHT) // 2
        
        self.reset_ball()
    
    def update(self, dt=1/60):
        if self.state.game_over:
            return
        
        self._update_paddles()
        self._update_ball()
        self._check_collisions()
        self._check_scoring()
        self._check_win_condition()
    
    def _update_paddles(self):
        # Paddle 1
        if self.state.paddle1.move_up:
            self.state.paddle1.y -= self.state.paddle1.speed
        if self.state.paddle1.move_down:
            self.state.paddle1.y += self.state.paddle1.speed
        
        # Paddle 2
        if self.state.paddle2.move_up:
            self.state.paddle2.y -= self.state.paddle2.speed
        if self.state.paddle2.move_down:
            self.state.paddle2.y += self.state.paddle2.speed
        
        # Giới hạn màn hình
        self.state.paddle1.y = max(0, min(SCREEN_HEIGHT - PADDLE_HEIGHT, self.state.paddle1.y))
        self.state.paddle2.y = max(0, min(SCREEN_HEIGHT - PADDLE_HEIGHT, self.state.paddle2.y))
    
    def _update_ball(self):
        self.state.ball.x += self.state.ball.vx
        self.state.ball.y += self.state.ball.vy
    
    def _check_collisions(self):
        ball = self.state.ball
        
        # Tường trên/dưới
        if ball.y <= 0 or ball.y >= SCREEN_HEIGHT - BALL_SIZE:
            ball.vy *= -1
            ball.y = max(0, min(SCREEN_HEIGHT - BALL_SIZE, ball.y))
        
        # Paddle 1
        if (ball.x <= self.state.paddle1.x + PADDLE_WIDTH and
            ball.x >= self.state.paddle1.x and
            ball.y + BALL_SIZE >= self.state.paddle1.y and
            ball.y <= self.state.paddle1.y + PADDLE_HEIGHT):
            
            ball.vx = abs(ball.vx)
            ball.x = self.state.paddle1.x + PADDLE_WIDTH
            relative_y = (ball.y - self.state.paddle1.y) / PADDLE_HEIGHT
            ball.vy = (relative_y - 0.5) * BALL_SPEED_Y * 2
            
            self._increase_ball_speed()
            self.ball_color = random.choice(BRIGHT_COLORS) # Đổi màu
        
        # Paddle 2
        if (ball.x + BALL_SIZE >= self.state.paddle2.x and
            ball.x <= self.state.paddle2.x + PADDLE_WIDTH and
            ball.y + BALL_SIZE >= self.state.paddle2.y and
            ball.y <= self.state.paddle2.y + PADDLE_HEIGHT):
            
            ball.vx = -abs(ball.vx)
            ball.x = self.state.paddle2.x - BALL_SIZE
            relative_y = (ball.y - self.state.paddle2.y) / PADDLE_HEIGHT
            ball.vy = (relative_y - 0.5) * BALL_SPEED_Y * 2
            
            self._increase_ball_speed()
            self.ball_color = random.choice(BRIGHT_COLORS) # Đổi màu
    
    def _increase_ball_speed(self):
        if abs(self.state.ball.vx) < BALL_MAX_SPEED:
            self.state.ball.vx *= 1.05
    
    def _check_scoring(self):
        ball = self.state.ball
        if ball.x < 0:
            self.state.score2 += 1
            self.reset_ball(direction=1)
        elif ball.x > SCREEN_WIDTH:
            self.state.score1 += 1
            self.reset_ball(direction=-1)
    
    def _check_win_condition(self):
        if self.state.score1 >= WINNING_SCORE:
            self.state.game_over = True
            self.state.winner = 1
        elif self.state.score2 >= WINNING_SCORE:
            self.state.game_over = True
            self.state.winner = 2
    
    def set_paddle_input(self, player_id, move_up, move_down):
        if player_id == 1:
            self.state.paddle1.move_up = move_up
            self.state.paddle1.move_down = move_down
        elif player_id == 2:
            self.state.paddle2.move_up = move_up
            self.state.paddle2.move_down = move_down
    
    def get_state(self):
        """
        SỬA LỖI: Trả về Object (self.state) thay vì Dictionary.
        Tuy nhiên, ta 'tiêm' thêm thuộc tính color vào object ball
        để khi chuyển sang JSON gửi đi, Client vẫn nhận được màu.
        """
        # Gán màu động vào object ball
        try:
            self.state.ball.color = self.ball_color
        except:
            pass # Phòng trường hợp ball không cho gán thuộc tính động
            
        # Trả về Object để Server Loop không bị crash
        return self.state