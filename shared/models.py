# shared/models.py
"""
Data models cho game objects
"""
from shared.constants import *

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = BALL_SPEED_X
        self.vy = BALL_SPEED_Y
        self.size = BALL_SIZE
    
    def to_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'vx': self.vx,
            'vy': self.vy
        }
    
    @staticmethod
    def from_dict(data):
        ball = Ball(data['x'], data['y'])
        ball.vx = data['vx']
        ball.vy = data['vy']
        return ball


class Paddle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.speed = PADDLE_SPEED
        self.move_up = False
        self.move_down = False
    
    def to_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        }
    
    @staticmethod
    def from_dict(data):
        paddle = Paddle(data['x'], data['y'])
        paddle.width = data['width']
        paddle.height = data['height']
        return paddle


class GameState:
    def __init__(self):
        self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.paddle1 = Paddle(PADDLE_OFFSET, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.paddle2 = Paddle(SCREEN_WIDTH - PADDLE_OFFSET - PADDLE_WIDTH, 
                             SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.score1 = 0
        self.score2 = 0
        self.game_over = False
        self.winner = None
    
    def to_dict(self):
        return {
            'ball': self.ball.to_dict(),
            'paddle1': self.paddle1.to_dict(),
            'paddle2': self.paddle2.to_dict(),
            'score1': self.score1,
            'score2': self.score2,
            'game_over': self.game_over,
            'winner': self.winner
        }
    
    @staticmethod
    def from_dict(data):
        state = GameState()
        state.ball = Ball.from_dict(data['ball'])
        state.paddle1 = Paddle.from_dict(data['paddle1'])
        state.paddle2 = Paddle.from_dict(data['paddle2'])
        state.score1 = data['score1']
        state.score2 = data['score2']
        state.game_over = data['game_over']
        state.winner = data['winner']
        return state