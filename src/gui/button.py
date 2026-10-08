from pathlib import Path

import pygame


class button:
    def __init__(self, path_img_norm, path_img_hover, position, size):
        assets_dir = Path(__file__).resolve().parents[2] / "assets" / "images"

        self.normal_img = pygame.image.load(assets_dir / path_img_norm)
        self.hover_img = pygame.image.load(assets_dir / path_img_hover)

        self.normal_img = pygame.transform.scale(self.normal_img, size)
        self.hover_img = pygame.transform.scale(self.hover_img, size)

        self.current_img = self.normal_img
        self.rect = self.current_img.get_rect(topleft=position)

    def update(self, mouse_position):
        if self.rect.collidepoint(mouse_position):
            self.current_img = self.hover_img
        else:
            self.current_img = self.normal_img

    def draw(self, screen):
        screen.blit(self.current_img, self.rect)

    def is_clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )
