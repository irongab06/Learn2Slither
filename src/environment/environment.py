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

	def step(self, action) :
		if action == "left":
			self.snake.turn_left()
		elif action == "right":
			self.snake.turn_right()
		next_head_position = self.snake.get_next_head_position()
		if not self.board.is_inside(next_head_position) :
			return False
		if self.snake.is_colliding_with_body(next_head_position) :
			return False
		apple = self.get_apple_at(next_head_position)
		grow = apple is not None and apple.apple_type == "green"
		self.snake.move(next_head_position, grow)
		if apple is not None and apple.apple_type == "red":
			self.snake.shrink()
			if not self.snake.body  :
				return False
		if apple is not None:
			self.apples.remove(apple)
			self.apples.append(self._create_random_apple(apple.apple_type))
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
