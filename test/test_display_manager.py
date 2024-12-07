from unittest import TestCase
from unittest.mock import Mock, patch

import mock.board
from mock.HD44780 import HD44780
from src.display_manager import DisplayManager

class TestDisplayManager(TestCase):

    @patch.object(HD44780, "lcd_string")
    def test_should_display_robot_position_no_obstacle_battery_percentage(self, mock_display: Mock):
        d = DisplayManager(mock.board.I2C())
        d.update_display_info((0,0,'N'), None, 20)
        mock_display.assert_called_once_with("R: (0,0,N) - O: ***** - B: 20%")

    @patch.object(HD44780, "lcd_string")
    def test_should_display_robot_position_obstacle_position_battery_percentage(self, mock_display: Mock):
        d = DisplayManager(mock.board.I2C())
        d.update_display_info((0,0,'N'), (0,1), 42)
        mock_display.assert_called_once_with("R: (0,0,N) - O: (0,1) - B: 42%")