import pygame
from pathlib import Path
from src.gui.button import button
from src.gui.selection_panel import SelectionPanel
from src.gui.ui_layout import (
	MODEL_ROW_CENTER_Y,
	MODEL_BUTTON_X,
	MODEL_BUTTON_WIDTH,
	MODEL_BUTTON_HEIGHT,
)
from src.gui.grid_renderer import GridRenderer
from src.environment.environment import Environment
from src.agent.agent import Agent

class Renderer:
	def __init__(self, agent=None, sessions=1, learn=False, speed=200,
	             step_by_step=False, grid_size=10):
		pygame.init()
		self.font = pygame.font.SysFont("futura", 28)
		self.big_font = pygame.font.SysFont("futura", 96)
		self._setup_windows()
		self._load_backgrounds()
		self._create_menu()
		self._create_button()

		self.page = "menu"
		self.running = True
		self.game_over = False
		self.clock = pygame.time.Clock()
		self.move_event = pygame.event.custom_type()
		self.move_delay = max(1, speed)
		self.step_by_step = step_by_step
		self.learn = learn
		self.sessions = sessions
		self.sessions_done = 0
		self.finished = False
		self.agent = agent
		if agent is not None:
			# Modele passe en argument : on saute le menu.
			self._create_grid(grid_size)
			self._start_game()

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
			self.grid.draw_apples(self.screen, self.environment.apples)
			self.grid.draw_snake(
				self.screen,
				self.environment.snake.body,
				self.environment.snake.direction,
			)
			self.draw_stats()
			if self.finished:
				self.draw_game_over()
		pygame.display.flip()

	def draw_game_over(self):
		center = (self.width // 2, self.height // 2)
		# Halo : le meme texte en rouge translucide, decale tout autour.
		halo = self.big_font.render("GAME OVER", True, (255, 0, 40))
		halo.set_alpha(70)
		for dx in (-4, 0, 4):
			for dy in (-4, 0, 4):
				rect = halo.get_rect(center=(center[0] + dx, center[1] + dy))
				self.screen.blit(halo, rect)
		text = self.big_font.render("GAME OVER", True, (255, 60, 60))
		self.screen.blit(text, text.get_rect(center=center))

	def draw_stats(self):
		cyan = (0, 229, 255)
		white = (255, 255, 255)
		if self.game_over:
			current_session = self.sessions_done
		else:
			current_session = self.sessions_done + 1
		stats = [
			("PARTIE", f"{current_session} / {self.sessions}"),
			("LONGUEUR", str(len(self.environment.snake.body))),
			("MAX", str(self.max_length)),
			("COUPS", str(self.steps)),
		]
		# Largeur de la colonne des libelles = le plus long d'entre eux.
		label_width = 0
		for label, _ in stats:
			label_width = max(label_width, self.font.size(label)[0])
		value_x = 36 + label_width + 24
		panel_width = value_x + 90
		# A gauche du plateau, aligne sur son bord haut.
		grid_x, grid_y = self.grid_position
		panel_x = max(20, grid_x - panel_width - 30)
		panel_y = grid_y
		y = panel_y + 12
		for label, value in stats:
			label_text = self.font.render(label, True, cyan)
			value_text = self.font.render(value, True, white)
			self.screen.blit(label_text, (panel_x + 16, y))
			self.screen.blit(value_text, (panel_x + value_x - 20, y))
			y += 40

	def run(self):
		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
					break
				if event.type == self.move_event:
					self.play_one_step()
				if event.type == pygame.KEYDOWN and self.step_by_step:
					if event.key in (pygame.K_SPACE, pygame.K_RIGHT):
						self.play_one_step()
				if self.page == "menu" and self.start_game.is_clicked(event):
					print("Start game clicked")
					self.page = "game_setup"
				for model_name in ["1", "10", "100", "best"]:
					if (
						self.page == "game_setup"
						and self.model_buttons[model_name].is_clicked(event)
					):
						if not self._load_model(model_name):
							continue
						self.selected_model = model_name
						self._create_grid(10)
						self._start_game()
			self.start_game.update(pygame.mouse.get_pos())
			for select in self.model_buttons.values() :
				select.update(pygame.mouse.get_pos())
			self.draw()
			self.clock.tick(60)
		pygame.time.set_timer(self.move_event, 0)
		pygame.quit()

	def _start_game(self):
		self.page = "game"
		self.game_over = False
		self.steps = 0
		self.max_length = len(self.environment.snake.body)
		self.state = self.environment.get_state()
		pygame.event.clear(self.move_event)
		if not self.step_by_step:
			pygame.time.set_timer(self.move_event, self.move_delay)

	def play_one_step(self):
		if self.page != "game" or self.finished:
			return
		if self.game_over:
			# La partie precedente est finie : on en lance une nouvelle.
			self.environment.reset()
			self._start_game()
			return

		action = self.agent.choose_action(self.state)
		self.environment.display_vision()
		print(f"Action : {action}")
		reward, self.game_over = self.environment.step(action)
		self.steps += 1
		self.max_length = max(
			self.max_length,
			len(self.environment.snake.body),
		)

		if self.game_over:
			next_state = None
		else:
			next_state = self.environment.get_state()

		if self.learn:
			self.agent.remember(
				self.state, action, reward, next_state, self.game_over
			)
			self.agent.train_step()
			self.agent.decay_epsilon()
		self.state = next_state

		if self.game_over:
			self._end_of_game()

	def _end_of_game(self):
		self.sessions_done += 1
		if self.environment.is_starving():
			print(
				f"Partie arretee : {self.environment.steps_without_apple} "
				f"coups sans pomme verte, "
				f"final length = {len(self.environment.snake.body)}, "
				f"max length = {self.max_length}, max duration = {self.steps}"
			)
		else:
			print(
				f"Game over, final length = {len(self.environment.snake.body)}, "
				f"max length = {self.max_length}, max duration = {self.steps}"
			)
		if self.sessions_done >= self.sessions:
			self.finished = True
			pygame.time.set_timer(self.move_event, 0)
			print("Toutes les parties sont terminees : fermez la fenetre.")
		elif not self.step_by_step:
			# Laisse le temps de lire "GAME OVER" avant la partie suivante.
			pygame.time.set_timer(self.move_event, 1500)

	def _load_model(self, model_name):
		if model_name == "best":
			file_name = "best.pth"
		else:
			file_name = f"{model_name}_sessions.pth"
		path = Path(__file__).resolve().parents[2] / "models" / file_name
		if not path.is_file():
			print(f"Modele introuvable : {path.name}")
			return False
		self.agent = Agent()
		self.agent.load(path)
		self.agent.epsilon = 0.0
		self.agent.network.eval()
		return True

	def _create_button(self) :
		self.start_game = button(
			"Start_game_blue.png",
			"Start_game_green.png",
			((self.width / 2) - 150, self.height * 0.78),
			(280, 120),
		)

		# Les boutons suivent le panneau, quelle que soit la taille de la fenetre.
		panel = self.model_panel.rect
		width = int(panel.width * MODEL_BUTTON_WIDTH)
		height = int(panel.height * MODEL_BUTTON_HEIGHT)
		x = panel.left + int(panel.width * MODEL_BUTTON_X)
		self.model_buttons = {}
		for model_name, center_y in MODEL_ROW_CENTER_Y.items():
			y = panel.top + int(panel.height * center_y) - height // 2
			self.model_buttons[model_name] = button(
				"Select_blue.png",
				"Select_red.png",
				(x, y),
				(width, height),
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
		self.grid_position = grid_position
		self.grid = GridRenderer(board_size, grid_position, size_grid)
		self.environment = Environment(
			size_grid,
			max_steps_without_apple=size_grid * size_grid,
		)
		self.game_over = False

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

if __name__ == "__main__":
	renderer = Renderer()
	renderer.run()
