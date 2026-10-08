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

    def left(self):
        self.direction = (-1, 0)

    def right(self):
        self.direction = (1, 0)

    def up(self):
            self.direction = (0, -1)

    def down(self):
        self.direction = (0, 1)

    def is_colliding_with_body(self, position) :
        return position in self.body
