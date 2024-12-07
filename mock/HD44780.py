from mock.board import I2C

class HD44780:
    I2C_ADDR = 0x27

    def __init__(self, i2c: I2C):
        pass

    def lcd_init(self):
        """
        Initializes the display
        """
        pass

    def lcd_string(self, message: str):
        """
        Writes a message on the display
        :param message: the message to display
        """
        pass

    def lcd_clear(self):
        pass