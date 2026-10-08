import pygame
from pathlib import Path


class GridRenderer:
    def __init__(self, board_size, position, size_grid):
        self.board_size = board_size
        self.grid_size = size_grid

        self.cell_size = self.board_size // size_grid
        assets_dir = Path(__file__).resolve().parents[2] / "assets" / "images"
        self.head_image = pygame.image.load(
            assets_dir / "head_up.png"
        ).convert_alpha()
        self.head_image = pygame.transform.smoothscale(
            self.head_image, (self.cell_size, self.cell_size)
        )
        self.tail_image = pygame.image.load(
            assets_dir / "tail_down.png"
        ).convert_alpha()
        self.tail_image = pygame.transform.smoothscale(
            self.tail_image, (self.cell_size, self.cell_size)
        )
        self.body_image = pygame.image.load(
            assets_dir / "body_vertical.png"
        ).convert_alpha()
        self.body_image = pygame.transform.smoothscale(
            self.body_image, (self.cell_size, self.cell_size)
        )
        self.corner_image = pygame.image.load(
            assets_dir / "body_corner_top_right.png"
        ).convert_alpha()
        self.corner_image = pygame.transform.smoothscale(
            self.corner_image, (self.cell_size, self.cell_size)
        )
        self.green_apple_image = pygame.image.load(
            assets_dir / "Green_apple.png"
        ).convert_alpha()
        self.green_apple_image = pygame.transform.smoothscale(
            self.green_apple_image, (self.cell_size, self.cell_size)
        )
        self.red_apple_image = pygame.image.load(
            assets_dir / "Red_apple.png"
        ).convert_alpha()
        self.red_apple_image = pygame.transform.smoothscale(
            self.red_apple_image, (self.cell_size, self.cell_size)
        )

        self.position = position

        self.rect = pygame.Rect(
            self.position[0],
            self.position[1],
            self.board_size,
            self.board_size,
        )

    def draw(self, screen) :
        # Halo extérieur
        frame_rect = self.rect.inflate(50, 50)
        frame_surface = pygame.Surface(
            frame_rect.size,
            pygame.SRCALPHA,
        )
        pygame.draw.rect(
            frame_surface,
            (0, 180, 220, 80),
            frame_surface.get_rect(),
            width=20,
        )
        screen.blit(frame_surface, frame_rect.topleft)

        # Fond de la grille
        pygame.draw.rect(
            screen,
            (3, 15, 32),
            self.rect,
        )
        
        self.create_grid(screen)

        # Contour cyan très lumineux
        pygame.draw.rect(
            screen,
            (0, 220, 255),
            self.rect,
            width=2,
        )

    def create_grid(self, screen):
        start_x = self.rect.left
        end_x = self.rect.right - 1

        start_y = self.rect.top
        end_y = self.rect.bottom - 1

        for line_number in range(1, self.grid_size) :
            offset = line_number * self.cell_size
            pygame.draw.line(
                screen,
                (0, 220, 255),
                (start_x, (start_y + offset)),
                (end_x, (start_y + offset)),
                1
            )
            pygame.draw.line(
                screen,
                (0, 220, 255),
                ((start_x + offset), start_y),
                ((start_x + offset), end_y),
                1
            )

    def draw_apples(self, screen, apples):
        for apple in apples:
            x, y = apple.position
            pixel_x = self.rect.left + x * self.cell_size
            pixel_y = self.rect.top + y * self.cell_size

            if apple.apple_type == "green":
                image = self.green_apple_image
            else:
                image = self.red_apple_image

            screen.blit(image, (pixel_x, pixel_y))

    def draw_snake(self, screen, body, direction):
        if not body:
            return
        size = len(body)

        for index in range(size):
            x, y = body[index]
            pixel_x = self.rect.left + x * self.cell_size
            pixel_y = self.rect.top + y * self.cell_size

            if index == 0:
                image = self.get_head_image(direction)
            elif index == size - 1:
                image = self.get_tail_image(body[index - 1], body[index])
            else:
                image = self.get_body_image(
                    body[index - 1], body[index], body[index + 1]
                )

            screen.blit(image, (pixel_x, pixel_y))

    def get_head_image(self, direction):
        x, y = direction
        if x == 0 and y == -1:
            return pygame.transform.rotate(self.head_image, 0)
        elif x == 0 and y == 1:
            return pygame.transform.rotate(self.head_image, 180)
        elif x == -1 and y == 0:
            return pygame.transform.rotate(self.head_image, 90)
        elif x == 1 and y == 0:
            return pygame.transform.rotate(self.head_image, -90)

    def get_body_image(self, previous_position, position, next_position):
        previous_x, previous_y = previous_position
        x, y = position
        next_x, next_y = next_position

        if previous_x == next_x:
            return self.body_image
        elif previous_y == next_y:
            return pygame.transform.rotate(self.body_image, 90)

        # Les voisins ne sont pas alignes : il faut un coude.
        up = previous_y < y or next_y < y
        down = previous_y > y or next_y > y
        left = previous_x < x or next_x < x
        right = previous_x > x or next_x > x

        if up and right:
            return pygame.transform.rotate(self.corner_image, 0)
        elif up and left:
            return pygame.transform.rotate(self.corner_image, 90)
        elif down and left:
            return pygame.transform.rotate(self.corner_image, 180)
        elif down and right:
            return pygame.transform.rotate(self.corner_image, -90)

    def get_tail_image(self, previous_position, position):
        previous_x, previous_y = previous_position
        x, y = position
        dx = previous_x - x
        dy = previous_y - y

        if dx == 0 and dy == -1:
            return pygame.transform.rotate(self.tail_image, 0)
        elif dx == 0 and dy == 1:
            return pygame.transform.rotate(self.tail_image, 180)
        elif dx == -1 and dy == 0:
            return pygame.transform.rotate(self.tail_image, 90)
        elif dx == 1 and dy == 0:
            return pygame.transform.rotate(self.tail_image, -90)
