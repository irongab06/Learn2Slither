import pygame


class GridRenderer:
	def __init__(self, size, position, size_grid):
		self.board_size = int(min(size) * 0.6)
		self.grid_size = size_grid

		self.cell_size = self.board_size // size_grid
		self.board_size = self.cell_size * self.grid_size

		self.position = position

		self.rect = pygame.Rect(
			self.position[0],
			self.position[1],
			self.board_size,
			self.board_size,
		)

	def draw(self, screen) :
		# Halo extérieur
		pygame.draw.rect(
			screen,
			(0, 70, 120),
			self.rect.inflate(14, 14),
			width=4,
		)

		# Contour bleu plus fort
		pygame.draw.rect(
			screen,
			(0, 150, 210),
			self.rect.inflate(6, 6),
			width=3,
		)

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
		start_x = self.position[0]
		end_x = self.position[0] + self.board_size

		start_y = self.position[1] 
		end_y = self.position[1] + self.board_size

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

