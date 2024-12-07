try:
    import HD44780
    import board
except:
    from mock.HD44780 import HD44780
    import mock.board

class DisplayManager:
    def __init__(self, i2c):
        self.display = HD44780(i2c)

    def update_display_info(self, robot_position: tuple[int, int, str], obstacle_position: tuple[int, int] or None, battery: int):
        pass
