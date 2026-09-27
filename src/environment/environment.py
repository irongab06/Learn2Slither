import random

from src.environment.apple import Apple
from src.environment.board import Board
from src.environment.snake import Snake

class Environment :
	def __init__(self, grid_size=10):
		direction = (0, -1)

		self.board = Board(grid_size)
		body = self.random_snake()
		self.snake = Snake(body, direction)
		self.apples = []
		self._create_apples()

	def get_state(self):
		vision = {
			"up": [],
			"down": [],
			"left": [],
			"right": [],
		}
		directions = {
			"up": (0, -1),
			"down": (0, 1),
			"left": (-1, 0),
			"right": (1, 0),
		}
		head_x, head_y = self.snake.body[0]

		for direction_name, (dx, dy) in directions.items():
			x = head_x + dx
			y = head_y + dy

			while self.board.is_inside((x, y)):
				position = (x, y)
				apple = self.get_apple_at(position)
				if position in self.snake.body:
					symbol = "S"
				elif apple is not None:
					if apple.apple_type == "green":
						symbol = "G"
					else:
						symbol = "R"
				else:
					symbol = "0"

				vision[direction_name].append(symbol)
				x += dx
				y += dy

			vision[direction_name].append("W")

		return vision

	def display_vision(self):
		vision = self.get_state()
		spaces = " " * len(vision["left"])

		# Afficher le haut depuis le mur jusqu'a la tete.
		position = len(vision["up"]) - 1
		while position >= 0:
			print(spaces + vision["up"][position])
			position -= 1

		position = len(vision["left"]) - 1
		while position >= 0:
			print(vision["left"][position], end="")
			position -= 1

		print("H", end="")
		for symbol in vision["right"]:
			print(symbol, end="")
		print()

		for symbol in vision["down"]:
			print(spaces + symbol)

	def random_snake(self):
		x = random.randrange(2, self.board.grid_size - 1)
		y = random.randrange(2, self.board.grid_size - 2)

		return [(x, y), (x, y + 1), (x, y + 2)]

	def reset(self):
		body = self.random_snake()
		direction = (0, -1)

		self.snake = Snake(body, direction)
		self.apples = []
		self._create_apples()

	def step(self, action) :
		reward = -0.1
		if action == "left":
			self.snake.left()
		elif action == "right":
			self.snake.right()
		elif action == "up":
			self.snake.up()
		elif action == "down":
			self.snake.down()
		next_head_position = self.snake.get_next_head_position()
		if not self.board.is_inside(next_head_position) :
			return -10, True
		if self.snake.is_colliding_with_body(next_head_position) :
			return -10, True
		apple = self.get_apple_at(next_head_position)
		grow = apple is not None and apple.apple_type == "green"
		self.snake.move(next_head_position, grow)
		if apple is not None and apple.apple_type == "red":
			self.snake.shrink()
			if not self.snake.body  :
				return -10, True
		if apple is not None:
			self.apples.remove(apple)
			self.apples.append(self._create_random_apple(apple.apple_type))
			if apple.apple_type == "green":
				reward = 1
			else:
				reward = -1
		return reward, False

	def _create_apples(self):
		for apple_type in ["green", "green", "red"]:
			self.apples.append(self._create_random_apple(apple_type))

	def _create_random_apple(self, apple_type):
		while True:
			position = (
				random.randrange(self.board.grid_size),
				random.randrange(self.board.grid_size),
			)
			is_on_snake = position in self.snake.body
			is_on_apple = any(
				position == apple.position for apple in self.apples
			)
			if not is_on_snake and not is_on_apple:
				return Apple(position, apple_type)

	def get_apple_at(self, next_head_position) :
		for apple in self.apples :
			if next_head_position == apple.position:
				return apple
		return None
