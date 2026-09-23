class Snake:
	def __init__(self, initial_body, direction):
		self.body = initial_body
		self.direction = direction

	def get_next_head_position(self):
		direction_x, direction_y = self.direction
		old_x, old_y = self.body[0]
		new_x = old_x + direction_x
		new_y = old_y + direction_y
		return (new_x, new_y)

	def move(self, next_head_position, grow):
		self.body.insert(0, next_head_position)
		if not grow:
			self.body.pop()

	def shrink(self):
		self.body.pop()

	def turn_left(self):
		x, y = self.direction

		if x == -1 and y == 0:
			x = 0
			y = 1
		elif x == 1 and y == 0:
			x = 0
			y = -1
		elif x == 0 and y == -1:
			x = -1
			y = 0
		elif x == 0 and y == 1:
			x = 1
			y = 0
		self.direction = (x, y)

	def turn_right(self):
		x, y = self.direction

		if x == -1 and y == 0:
			x = 0
			y = -1
		elif x == 1 and y == 0:
			x = 0
			y = 1
		elif x == 0 and y == -1:
			x = 1
			y = 0
		elif x == 0 and y == 1:
			x = -1
			y = 0
		self.direction = (x, y)

	def is_colliding_with_body(self, position) :
		return position in self.body
