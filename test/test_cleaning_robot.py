from unittest import TestCase
from unittest.mock import Mock, patch, call

from mock import GPIO
from mock.ibs import IBS
from src.cleaning_robot import CleaningRobot, CleaningRobotError


class TestCleaningRobot(TestCase):

    def test_should_reset_robot_position(self):
        c = CleaningRobot()
        c.initialize_robot()
        self.assertEqual(c.robot_status(), "(0,0,N)")

    @patch.object(GPIO, "output")
    @patch.object(IBS, "get_charge_left")
    def test_should_turn_off_the_cleaning_system_and_turn_on_the_led_when_battery_lower_than_10(self, mock_ibs: Mock, mock_gpio: Mock):
        c = CleaningRobot()
        mock_ibs.return_value = 5
        c.manage_cleaning_system()
        mock_gpio.assert_has_calls([call(c.CLEANING_SYSTEM_PIN, GPIO.LOW), call(c.RECHARGE_LED_PIN, GPIO.HIGH)])

    @patch.object(GPIO, "output")
    @patch.object(IBS, "get_charge_left")
    def test_should_turn_on_the_cleaning_system_and_turn_off_the_led_when_battery_greater_than_10(self, mock_ibs: Mock, mock_gpio: Mock):
        c = CleaningRobot()
        mock_ibs.return_value = 12
        c.manage_cleaning_system()
        mock_gpio.assert_has_calls([call(c.CLEANING_SYSTEM_PIN, GPIO.HIGH), call(c.RECHARGE_LED_PIN, GPIO.LOW)])

    def test_should_move_forward(self):
        c = CleaningRobot()
        c.initialize_robot()
        c.execute_command(c.FORWARD)
        self.assertEqual(c.robot_status(), "(0,1,N)")

    def test_should_move_left(self):
        c = CleaningRobot()
        c.initialize_robot()
        c.execute_command(c.LEFT)
        self.assertEqual(c.robot_status(), "(0,0,W)")

    def test_should_rotate_right(self):
        c = CleaningRobot()
        c.initialize_robot()
        c.execute_command(c.RIGHT)
        self.assertEqual(c.robot_status(), "(0,0,E)")

    def test_should_raise_error_on_invalid_movement_command(self):
        c = CleaningRobot()
        c.initialize_robot()
        self.assertRaises(CleaningRobotError, c.execute_command, "U")
