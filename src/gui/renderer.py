from pathlib import Path

import pygame

class Renderer:
	def __init__(self) :
		pygame.init()

		info = pygame.display.Info()

		screen_width = info.current_w
		screen_height = info.current_h

		self.width = int(screen_width * 0.6)
		self.height = int(screen_height * 0.6)

		self.screen = pygame.display.set_mode((self.width, self.height))
		pygame.display.set_caption("learn2slither")

		assets_dir = Path(__file__).resolve().parents[2] / "assets" / "images"
		self.background = pygame.image.load(assets_dir / "Background.png").convert()
		self.background = pygame.transform.scale(self.background, (self.width, self.height))

		self.running = True
	def draw(self):
		self.screen.blit(self.background, (0, 0))
		pygame.display.flip()

	def run(self):
		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
			self.draw()
		pygame.quit()

renderer = Renderer()
renderer.run()
