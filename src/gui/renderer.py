import pygame
from pathlib import Path
from src.gui.button import button
from src.gui.selection_panel import SelectionPanel
from src.gui.ui_layout import MODEL_BUTTON_POSITION, MODEL_BUTTON_SIZE
from src.gui.grid_renderer import GridRenderer

class Renderer:
	def __init__(self) :
		pygame.init()
		self._setup_windows()
		self._load_backgrounds()
		self._create_button()
		self._create_menu()

		self.page = "menu"
		self.running = True

	def draw(self):
		if self.page == "menu" :
			self.screen.blit(self.background, (0, 0))
			self.start_game.draw(self.screen)
		elif self.page == "game_setup" :
			self.screen.blit(self.background_game, (0, 0))
			self.model_panel.draw(self.screen)
			for select in self.model_buttons.values() :
				select.draw(self.screen)
		elif self.page == "game" :
			self.screen.blit(self.background_game, (0, 0))
			self.grid.draw(self.screen)
		pygame.display.flip()

	def run(self):
		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
				if self.start_game.is_clicked(event) :
					print("Start game clicked")
					self.page = "game_setup"
				for model_name in ["1", "10", "100", "best"]:
					if (
						self.page == "game_setup"
						and self.model_buttons[model_name].is_clicked(event)
					):
						self.selected_model = model_name
						self._create_grid(10)
						self.page = "game"
			self.start_game.update(pygame.mouse.get_pos())
			for select in self.model_buttons.values() :
				select.update(pygame.mouse.get_pos())
			self.draw()
		pygame.quit()

	def _create_button(self) :
		self.start_game = button(
			"Start_game_blue.png",
			"Start_game_green.png",
			((self.width / 2) - 150, self.height * 0.78),
			(280, 120),
		)

		model_choices = ["1", "10", "100", "best", "bonus"]
		self.model_buttons = {}
		for index, model_name in enumerate(model_choices):
			self.model_buttons[model_name] = button(
				"Select_blue.png",
				"Select_red.png",
				MODEL_BUTTON_POSITION[model_name],
				MODEL_BUTTON_SIZE,
			)

	def _create_grid(self, size_grid) :
		grid_size = (self.width, self.height)
		coef_size = 0.6
		if size_grid > 10:
			coef_size = 0.8
		board_size = int(min(grid_size) * coef_size)
		cell_size = board_size // size_grid
		board_size = cell_size * size_grid

		grid_position = (
			(self.width - board_size) // 2,
			(self.height - board_size) // 2,
		)
		self.grid = GridRenderer(board_size, grid_position, size_grid)

	def _create_menu(self):
		panel_height = int(self.height * 0.8)
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

	def _load_backgrounds(self):
		assets_dir = Path(__file__).resolve().parents[2] / "assets" / "images"
		self.background = pygame.image.load(assets_dir / "Background.png").convert()
		self.background = pygame.transform.scale(self.background, (self.width, self.height))

		self.background_game = pygame.image.load(assets_dir / "Background_game.png").convert()
		self.background_game = pygame.transform.scale(self.background_game, (self.width, self.height))

	def _setup_windows(self) :
		info = pygame.display.Info()

		screen_width = info.current_w
		screen_height = info.current_h

		self.width = int(screen_width * 0.8)
		self.height = int(screen_height * 0.8)

		self.screen = pygame.display.set_mode((self.width, self.height))
		pygame.display.set_caption("learn2slither")

renderer = Renderer()
renderer.run()
