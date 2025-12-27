# server/ai_player.py
"""
AI Player logic
"""
import random
import time
from shared.constants import *

class AIPlayer:
    def __init__(self, difficulty="medium"):
        """
        difficulty: "easy", "medium", "hard"
        """
        self.difficulty = difficulty
        self.last_move_time = 0
        self.reaction_delay = AI_REACTION_DELAY
        
        # Set độ chính xác theo difficulty
        if difficulty == "easy":
            self.accuracy = AI_DIFFICULTY_EASY
            self.reaction_delay = 0.1
        elif difficulty == "hard":
            self.accuracy = AI_DIFFICULTY_HARD
            self.reaction_delay = 0.02
        else:  # medium
            self.accuracy = AI_DIFFICULTY_MEDIUM
            self.reaction_delay = 0.05
    
    def calculate_move(self, game_state):
        """
        Tính toán move của AI dựa trên game state
        Returns: (move_up, move_down)
        """
        current_time = time.time()
        
        # Thêm delay để AI không phản ứng tức thì
        if current_time - self.last_move_time < self.reaction_delay:
            return False, False
        
        ball = game_state.ball
        paddle = game_state.paddle2  # AI là player 2
        
        # Tính target position (nơi AI muốn di chuyển paddle đến)
        target_y = self._predict_ball_position(game_state)
        
        # Thêm random error dựa trên difficulty
        if random.random() > self.accuracy:
            # AI đôi khi miss
            error = random.randint(-50, 50)
            target_y += error
        
        # Tính toán paddle center
        paddle_center = paddle.y + PADDLE_HEIGHT / 2
        
        # Dead zone - không cần di chuyển nếu đã gần target
        dead_zone = 15
        
        move_up = False
        move_down = False
        
        if target_y < paddle_center - dead_zone:
            move_up = True
        elif target_y > paddle_center + dead_zone:
            move_down = True
        
        self.last_move_time = current_time
        return move_up, move_down
    
    def _predict_ball_position(self, game_state):
        """
        Dự đoán vị trí bóng sẽ đến paddle của AI
        """
        ball = game_state.ball
        paddle = game_state.paddle2
        
        # Nếu bóng đang bay ra xa AI, target vào giữa màn hình
        if ball.vx < 0:  # Bay sang trái (ra xa AI)
            return SCREEN_HEIGHT / 2
        
        # Predict đơn giản: giả sử bóng bay thẳng
        # Tính thời gian để bóng đến paddle
        distance_to_paddle = paddle.x - ball.x
        
        if ball.vx == 0:
            return ball.y
        
        time_to_reach = distance_to_paddle / ball.vx
        
        # Predict y position
        predicted_y = ball.y + (ball.vy * time_to_reach)
        
        # Xử lý bounce với top/bottom
        while predicted_y < 0 or predicted_y > SCREEN_HEIGHT:
            if predicted_y < 0:
                predicted_y = -predicted_y
            elif predicted_y > SCREEN_HEIGHT:
                predicted_y = 2 * SCREEN_HEIGHT - predicted_y
        
        return predicted_y
    
    def set_difficulty(self, difficulty):
        """Thay đổi độ khó"""
        self.difficulty = difficulty
        if difficulty == "easy":
            self.accuracy = AI_DIFFICULTY_EASY
            self.reaction_delay = 0.1
        elif difficulty == "hard":
            self.accuracy = AI_DIFFICULTY_HARD
            self.reaction_delay = 0.02
        else:
            self.accuracy = AI_DIFFICULTY_MEDIUM
            self.reaction_delay = 0.05