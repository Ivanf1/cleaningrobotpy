class Room:
    def __init__(self, x, y):
        if x is not None:
            self.max_x = x
        else:
            self.max_x = 2

        if y is not None:
            self.max_y = y
        else:
            self.max_y = 2

    def is_position_valid(self, position: tuple[int, int]) -> bool:
        x, y = position
        return 0 <= x <= self.max_x and 0 <= y <= self.max_y