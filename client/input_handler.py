# client/input_handler.py
"""
Xử lý input từ người chơi
"""
import pygame
from shared.constants import *

class InputHandler:
    def __init__(self):
        self.move_up = False
        self.move_down = False
        self.quit_game = False
        self.enter_pressed = False
        self.escape_pressed = False
        self.space_pressed = False  # Thêm space cho play again
    
    def process_events(self):
        """Xử lý tất cả pygame events"""
        self.enter_pressed = False
        self.escape_pressed = False
        self.space_pressed = False  # Reset space
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game = True
            
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)
            
            elif event.type == pygame.KEYUP:
                self._handle_keyup(event.key)
    
    def _handle_keydown(self, key):
        """Xử lý phím nhấn xuống"""
        # Player 1 controls (W/S)
        if key == pygame.K_w:
            self.move_up = True
        elif key == pygame.K_s:
            self.move_down = True
        
        # Alternative controls (Arrow keys)
        elif key == pygame.K_UP:
            self.move_up = True
        elif key == pygame.K_DOWN:
            self.move_down = True
        
        # Menu controls
        elif key == pygame.K_RETURN:
            self.enter_pressed = True
        elif key == pygame.K_ESCAPE:
            self.escape_pressed = True
        elif key == pygame.K_SPACE:
            self.space_pressed = True
    
    def _handle_keyup(self, key):
        """Xử lý phím thả ra"""
        if key == pygame.K_w or key == pygame.K_UP:
            self.move_up = False
        elif key == pygame.K_s or key == pygame.K_DOWN:
            self.move_down = False
    
    def get_movement(self):
        """Lấy trạng thái di chuyển hiện tại"""
        return self.move_up, self.move_down
    
    def should_quit(self):
        """Kiểm tra có quit không"""
        return self.quit_game or self.escape_pressed
    
    def is_enter_pressed(self):
        """Kiểm tra Enter có được nhấn không"""
        return self.enter_pressed
    
    def is_space_pressed(self):
        """Kiểm tra Space có được nhấn không"""
        return self.space_pressed
    
    def reset(self):
        """Reset input state"""
        self.move_up = False
        self.move_down = False
        self.quit_game = False
        self.enter_pressed = False
        self.escape_pressed = False
        self.space_pressed = False