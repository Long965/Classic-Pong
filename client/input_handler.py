# client/input_handler.py
import pygame

class InputHandler:
    def __init__(self):
        pass

    def get_input_data(self):
        """
        Kiểm tra trực tiếp trạng thái bàn phím.
        Trả về: (move_up, move_down)
        """
        keys = pygame.key.get_pressed()
        
        move_up = False
        move_down = False
        
        # Hỗ trợ cả phím Mũi tên và W/S
        # K_UP / K_w : Đi lên (y giảm)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move_up = True
            
        # K_DOWN / K_s : Đi xuống (y tăng)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move_down = True
            
        return move_up, move_down