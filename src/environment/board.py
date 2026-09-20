class Board:
	def __init__(self, grid_size):
		self.grid_size = grid_size

	def is_inside(self,position):
		x, y = position
		if (
			x < 0
			or y < 0
			or x >= self.grid_size
			or y >= self.grid_size
		):
			return False
		return True