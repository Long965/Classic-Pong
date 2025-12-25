import pygame
from shared.constants import WHITE, SCREEN_WIDTH

class UI:
    @staticmethod
    def show_message(screen, text, font, y_offset=0):
        surf = font.render(text, True, WHITE)
        rect = surf.get_rect(center=(SCREEN_WIDTH // 2, (screen.get_height() // 2) + y_offset))
        screen.blit(surf, rect)