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

	def move(self, next_head_position) :
		self.body.insert(0, next_head_position)
		self.body.pop()