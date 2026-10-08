import pygame
from pathlib import Path


class SelectionPanel:
    def __init__(self, path_img, position, size):
        assets_dir = Path(__file__).resolve().parents[2] / "assets" / "images"

        self.img = pygame.image.load(assets_dir / path_img)

        self.img = pygame.transform.scale(self.img, size)

        self.rect = self.img.get_rect(topleft=position)

    def draw(self, screen):
        screen.blit(self.img, self.rect)
