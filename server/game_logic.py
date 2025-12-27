# server/game_logic.py
"""
Logic game: vật lý, va chạm, tính điểm
"""
import random
from shared.models import GameState
from shared.constants import *

class GameLogic:
    def __init__(self):
        self.state = GameState()
        self.reset_ball()
    
    def reset_ball(self, direction=None):
        """Reset bóng về giữa màn hình"""
        self.state.ball.x = SCREEN_WIDTH // 2
        self.state.ball.y = SCREEN_HEIGHT // 2
        
        # Random hướng bay
        if direction is None:
            direction = random.choice([-1, 1])
        
        self.state.ball.vx = BALL_SPEED_X * direction
        self.state.ball.vy = random.uniform(-BALL_SPEED_Y, BALL_SPEED_Y)

    def reset_game(self):
        """Reset toàn bộ trạng thái game về 0-0"""
        self.state.score1 = 0
        self.state.score2 = 0
        self.state.game_over = False
        self.state.winner = None
        
        # Reset vị trí paddles
        self.state.paddle1.y = (SCREEN_HEIGHT - PADDLE_HEIGHT) // 2
        self.state.paddle2.y = (SCREEN_HEIGHT - PADDLE_HEIGHT) // 2
        
        # Reset bóng
        self.reset_ball()
    # ----------------------------------
    
    def update(self, dt=1/60):
        """Update game logic"""
        if self.state.game_over:
            return
        
        # Update paddle positions
        self._update_paddles()
        
        # Update ball position
        self._update_ball()
        
        # Check collisions
        self._check_collisions()
        
        # Check scoring
        self._check_scoring()
        
        # Check win condition
        self._check_win_condition()
    
    def _update_paddles(self):
        """Update vị trí paddles"""
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
        
        # Giới hạn trong màn hình
        self.state.paddle1.y = max(0, min(SCREEN_HEIGHT - PADDLE_HEIGHT, self.state.paddle1.y))
        self.state.paddle2.y = max(0, min(SCREEN_HEIGHT - PADDLE_HEIGHT, self.state.paddle2.y))
    
    def _update_ball(self):
        """Update vị trí bóng"""
        self.state.ball.x += self.state.ball.vx
        self.state.ball.y += self.state.ball.vy
    
    def _check_collisions(self):
        """Kiểm tra va chạm"""
        ball = self.state.ball
        
        # Va chạm với top/bottom
        if ball.y <= 0 or ball.y >= SCREEN_HEIGHT - BALL_SIZE:
            ball.vy *= -1
            ball.y = max(0, min(SCREEN_HEIGHT - BALL_SIZE, ball.y))
        
        # Va chạm với paddle 1
        if (ball.x <= self.state.paddle1.x + PADDLE_WIDTH and
            ball.x >= self.state.paddle1.x and
            ball.y + BALL_SIZE >= self.state.paddle1.y and
            ball.y <= self.state.paddle1.y + PADDLE_HEIGHT):
            
            ball.vx = abs(ball.vx)  # Đảm bảo bay sang phải
            ball.x = self.state.paddle1.x + PADDLE_WIDTH
            
            # Thay đổi góc dựa vào vị trí va chạm
            relative_y = (ball.y - self.state.paddle1.y) / PADDLE_HEIGHT
            ball.vy = (relative_y - 0.5) * BALL_SPEED_Y * 2
            
            # Tăng tốc độ nhẹ
            self._increase_ball_speed()
        
        # Va chạm với paddle 2
        if (ball.x + BALL_SIZE >= self.state.paddle2.x and
            ball.x <= self.state.paddle2.x + PADDLE_WIDTH and
            ball.y + BALL_SIZE >= self.state.paddle2.y and
            ball.y <= self.state.paddle2.y + PADDLE_HEIGHT):
            
            ball.vx = -abs(ball.vx)  # Đảm bảo bay sang trái
            ball.x = self.state.paddle2.x - BALL_SIZE
            
            # Thay đổi góc
            relative_y = (ball.y - self.state.paddle2.y) / PADDLE_HEIGHT
            ball.vy = (relative_y - 0.5) * BALL_SPEED_Y * 2
            
            # Tăng tốc độ nhẹ
            self._increase_ball_speed()
    
    def _increase_ball_speed(self):
        """Tăng tốc độ bóng sau mỗi lần chạm paddle"""
        if abs(self.state.ball.vx) < BALL_MAX_SPEED:
            self.state.ball.vx *= 1.05
    
    def _check_scoring(self):
        """Kiểm tra ghi điểm"""
        ball = self.state.ball
        
        # Player 2 ghi điểm (ball ra ngoài bên trái)
        if ball.x < 0:
            self.state.score2 += 1
            self.reset_ball(direction=1)  # Bay sang phải
        
        # Player 1 ghi điểm (ball ra ngoài bên phải)
        elif ball.x > SCREEN_WIDTH:
            self.state.score1 += 1
            self.reset_ball(direction=-1)  # Bay sang trái
    
    def _check_win_condition(self):
        """Kiểm tra điều kiện thắng"""
        if self.state.score1 >= WINNING_SCORE:
            self.state.game_over = True
            self.state.winner = 1
        elif self.state.score2 >= WINNING_SCORE:
            self.state.game_over = True
            self.state.winner = 2
    
    def set_paddle_input(self, player_id, move_up, move_down):
        """Set input cho paddle"""
        if player_id == 1:
            self.state.paddle1.move_up = move_up
            self.state.paddle1.move_down = move_down
        elif player_id == 2:
            self.state.paddle2.move_up = move_up
            self.state.paddle2.move_down = move_down
    
    def get_state(self):
        """Lấy game state hiện tại"""
        return self.state