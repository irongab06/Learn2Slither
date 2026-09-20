import pygame


class GridRenderer:
	def __init__(self, board_size, position, size_grid):
		self.board_size = board_size
		self.grid_size = size_grid

		self.cell_size = self.board_size // size_grid

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
