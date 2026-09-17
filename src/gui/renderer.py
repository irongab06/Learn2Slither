import pygame
from pathlib import Path
from src.gui.button import button
from src.gui.selection_panel import SelectionPanel

class Renderer:
	def __init__(self) :
		pygame.init()

		info = pygame.display.Info()

		self.start_game = button("Start_game_blue.png",
							"Start_game_green.png",
							(400, 550),
							(250, 80),
		)

		self.page = "menu"

		screen_width = info.current_w
		screen_height = info.current_h

		self.width = int(screen_width * 0.6)
		self.height = int(screen_height * 0.6)

		panel_height = int(self.height * 0.78)
		panel_width = int(panel_height * 1122 / 1402)

		panel_size = (panel_width, panel_height)
		panel_position = (
			(self.width - panel_width) // 2,
			(self.height - panel_height) // 2,
		)

		self.model_panel = SelectionPanel(
			"Select_model.png",
			panel_position,
			panel_size,
		)

		self.screen = pygame.display.set_mode((self.width, self.height))
		pygame.display.set_caption("learn2slither")

		assets_dir = Path(__file__).resolve().parents[2] / "assets" / "images"
		self.background = pygame.image.load(assets_dir / "Background.png").convert()
		self.background = pygame.transform.scale(self.background, (self.width, self.height))

		self.background_game = pygame.image.load(assets_dir / "Background_game.png").convert()
		self.background_game = pygame.transform.scale(self.background_game, (self.width, self.height))

		self.running = True

	def draw(self):
		if self.page == "menu" :
			self.screen.blit(self.background, (0, 0))
			self.start_game.draw(self.screen)
		if self.page == "game_setup" :
			self.screen.blit(self.background_game, (0, 0))
			self.model_panel.draw(self.screen)
		pygame.display.flip()

	def run(self):
		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
				if self.start_game.is_clicked(event) :
					print("Start game clicked")
					self.page = "game_setup"

			self.start_game.update(pygame.mouse.get_pos())
			self.draw()
		pygame.quit()

renderer = Renderer()
renderer.run()