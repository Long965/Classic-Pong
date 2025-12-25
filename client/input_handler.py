import pygame

class InputHandler:
    def __init__(self):
        # Trạng thái phím bấm
        self.move_up = False
        self.move_down = False

    def update(self):
        """Cập nhật trạng thái phím từ Pygame events"""
        keys = pygame.key.get_pressed()
        # Hỗ trợ cả phím mũi tên và W/S
        self.move_up = keys[pygame.K_UP] or keys[pygame.K_w]
        self.move_down = keys[pygame.K_DOWN] or keys[pygame.K_s]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def get_input_data(self):
        return self.move_up, self.move_down