# client/ui.py
"""
UI components: Menu, screens
"""
import pygame
from client.renderer import Renderer
from client.input_handler import InputHandler

class UI:
    def __init__(self):
        self.renderer = Renderer()
        self.input_handler = InputHandler()
        self.current_screen = "menu"  # menu, connecting, waiting, playing, game_over, disconnected
    
    def show_main_menu(self):
        """Hiển thị main menu"""
        options = ["Multiplayer (2 Players)", "Play vs AI", "Exit"]
        selected = 0
        
        while True:
            self.input_handler.process_events()
            
            if self.input_handler.should_quit():
                return "exit"
            
            # Get input state
            move_up, move_down = self.input_handler.get_movement()
            
            # Menu navigation
            if move_up and selected > 0:
                selected -= 1
                pygame.time.wait(150)  # Debounce
            elif move_down and selected < len(options) - 1:
                selected += 1
                pygame.time.wait(150)  # Debounce
            
            # Handle selection
            if self.input_handler.is_enter_pressed():
                if selected == 0:
                    return "multiplayer"
                elif selected == 1:
                    return "ai_mode"
                else:
                    return "exit"
            
            # Draw menu
            self.renderer.draw_menu("CLASSIC PONG", options, selected)
            self.renderer.update()
    
    def show_ai_difficulty_menu(self):
        """Hiển thị menu chọn độ khó AI"""
        options = ["Easy", "Medium", "Hard", "Back"]
        selected = 1  # Default: Medium
        
        while True:
            self.input_handler.process_events()
            
            if self.input_handler.should_quit():
                return None
            
            # Get input state
            move_up, move_down = self.input_handler.get_movement()
            
            # Menu navigation
            if move_up and selected > 0:
                selected -= 1
                pygame.time.wait(150)
            elif move_down and selected < len(options) - 1:
                selected += 1
                pygame.time.wait(150)
            
            # Handle selection
            if self.input_handler.is_enter_pressed():
                if selected == 0:
                    return "easy"
                elif selected == 1:
                    return "medium"
                elif selected == 2:
                    return "hard"
                else:
                    return None  # Back
            
            # Draw menu
            self.renderer.draw_menu("SELECT DIFFICULTY", options, selected)
            self.renderer.update()
    
    def show_connecting(self):
        """Hiển thị màn hình connecting"""
        self.renderer.draw_connecting()
        self.renderer.update()
    
    def show_waiting(self):
        """Hiển thị màn hình waiting"""
        self.current_screen = "waiting"
        while self.current_screen == "waiting":
            self.input_handler.process_events()
            
            if self.input_handler.should_quit():
                return False
            
            self.renderer.draw_waiting()
            self.renderer.update()
        
        return True
    
    def show_game(self, game_state, player_id):
        """Hiển thị game"""
        self.renderer.draw_game(game_state, player_id)
        self.renderer.update()
    
    def show_game_over(self, winner, player_id):
        """Hiển thị game over dạng menu"""
        self.current_screen = "game_over"
        selected = 0
        options = ["play_again", "menu"] # Các hành động trả về tương ứng
        
        self.input_handler.reset() # Xóa trạng thái phím cũ
        
        while self.current_screen == "game_over":
            self.input_handler.process_events()
            
            if self.input_handler.should_quit():
                return "exit"
            
            # Xử lý di chuyển lên xuống
            move_up, move_down = self.input_handler.get_movement()
            if move_up and selected > 0:
                selected -= 1
                pygame.time.wait(150)
            elif move_down and selected < len(options) - 1:
                selected += 1
                pygame.time.wait(150)
            
            # Xử lý chọn
            if self.input_handler.is_enter_pressed():
                return options[selected]
            
            # Vẽ Game Over kèm menu lựa chọn
            self.renderer.draw_game_over(winner, player_id, selected)
            self.renderer.update()
        
        return "exit"
    
    def show_disconnected(self):
        """Hiển thị màn hình disconnected"""
        self.current_screen = "disconnected"
        while self.current_screen == "disconnected":
            self.input_handler.process_events()
            
            if self.input_handler.should_quit():
                return
            
            self.renderer.draw_disconnected()
            self.renderer.update()
    
    def set_screen(self, screen_name):
        """Set current screen"""
        self.current_screen = screen_name
    
    def cleanup(self):
        """Cleanup UI"""
        self.renderer.quit()