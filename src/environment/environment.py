import random

from src.environment.apple import Apple
from src.environment.board import Board
from src.environment.snake import Snake

class Environment :
	def __init__(self, grid_size=10):
		body = [(5, 5), (5, 6), (5, 7)]
		direction = (0, -1)

		self.board = Board(grid_size)
		self.snake = Snake(body, direction)
		self.apples = []
		self._create_apples()

	def step(self) :
		next_head_position = self.snake.get_next_head_position()
		if not self.board.is_inside(next_head_position) :
			return False
		if self.snake.is_colliding_with_body(next_head_position) :
			return False
		self.snake.move(next_head_position)
		return True

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