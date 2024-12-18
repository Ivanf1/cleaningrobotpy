from unittest import TestCase
from unittest.mock import Mock, patch, call

from mock import GPIO
from mock.ibs import IBS
from src.cleaning_robot import CleaningRobot, CleaningRobotError
from src.display_manager import DisplayManager
from src.room import Room


class TestCleaningRobot(TestCase):

    def test_should_reset_robot_position(self):
        r = Room(2, 2)
        c = CleaningRobot(r)
        c.initialize_robot()
        self.assertEqual(c.robot_status(), "(0,0,N)")

    @patch.object(GPIO, "output")
    @patch.object(IBS, "get_charge_left")
    def test_should_turn_off_the_cleaning_system_and_turn_on_the_led_when_battery_lower_than_10(self, mock_ibs: Mock, mock_gpio: Mock):
        r = Room(2, 2)
        c = CleaningRobot(r)
        mock_ibs.return_value = 5
        c.manage_cleaning_system()
        mock_gpio.assert_has_calls([call(c.CLEANING_SYSTEM_PIN, GPIO.LOW), call(c.RECHARGE_LED_PIN, GPIO.HIGH)])

    @patch.object(GPIO, "output")
    @patch.object(IBS, "get_charge_left")
    def test_should_turn_on_the_cleaning_system_and_turn_off_the_led_when_battery_greater_than_10(self, mock_ibs: Mock, mock_gpio: Mock):
        r = Room(2, 2)
        c = CleaningRobot(r)
        mock_ibs.return_value = 12
        c.manage_cleaning_system()
        mock_gpio.assert_has_calls([call(c.CLEANING_SYSTEM_PIN, GPIO.HIGH), call(c.RECHARGE_LED_PIN, GPIO.LOW)])

    @patch.object(IBS, "get_charge_left")
    def test_should_move_forward(self, mock_ibs: Mock):
        r = Room(2, 2)
        c = CleaningRobot(r)
        c.initialize_robot()
        mock_ibs.return_value = 12
        c.execute_command(c.FORWARD)
        self.assertEqual(c.robot_status(), "(0,1,N)")

    @patch.object(IBS, "get_charge_left")
    def test_should_move_left(self, mock_ibs: Mock):
        r = Room(2, 2)
        c = CleaningRobot(r)
        c.initialize_robot()
        mock_ibs.return_value = 12
        c.execute_command(c.LEFT)
        self.assertEqual(c.robot_status(), "(0,0,W)")

    @patch.object(IBS, "get_charge_left")
    def test_should_rotate_right(self, mock_ibs: Mock):
        r = Room(2, 2)
        c = CleaningRobot(r)
        c.initialize_robot()
        mock_ibs.return_value = 12
        c.execute_command(c.RIGHT)
        self.assertEqual(c.robot_status(), "(0,0,E)")

    @patch.object(IBS, "get_charge_left")
    def test_should_raise_error_on_invalid_movement_command(self, mock_ibs: Mock):
        r = Room(2, 2)
        c = CleaningRobot(r)
        c.initialize_robot()
        mock_ibs.return_value = 12
        self.assertRaises(CleaningRobotError, c.execute_command, "U")

    @patch.object(IBS, "get_charge_left")
    def test_should_raise_error_on_invalid_movement_out_of_bound(self, mock_ibs: Mock):
        r = Room(2, 2)
        c = CleaningRobot(r)
        c.initialize_robot()
        mock_ibs.return_value = 12
        c.execute_command(c.LEFT)
        self.assertRaises(CleaningRobotError, c.execute_command, c.FORWARD)

    @patch.object(IBS, "get_charge_left")
    @patch.object(GPIO, "input")
    def test_should_not_move_forward_if_obstacle_found(self, mock_gpio: Mock, mock_ibs: Mock):
        r = Room(2, 2)
        c = CleaningRobot(r)
        c.initialize_robot()
        mock_gpio.return_value = True
        mock_ibs.return_value = 12
        self.assertEqual(c.execute_command(c.FORWARD), "(0,0,N),(0,1)")

    @patch.object(IBS, "get_charge_left")
    def test_should_turn_on_the_cleaning_system_and_turn_off_the_led(self, mock_ibs: Mock):
        r = Room(2, 2)
        c = CleaningRobot(r)
        mock_ibs.return_value = 9
        c.initialize_robot()
        self.assertEqual(c.execute_command(c.FORWARD), "!(0,0,N)")

    @patch.object(GPIO, "output")
    @patch.object(IBS, "get_charge_left")
    @patch.object(GPIO, "input")
    def test_should_trigger_the_buzzer_if_obstacle_found(self, mock_gpio: Mock, mock_ibs: Mock, mock_buzzer: Mock):
        r = Room(2, 2)
        c = CleaningRobot(r)
        c.initialize_robot()
        mock_gpio.return_value = True
        mock_ibs.return_value = 12
        c.execute_command(c.FORWARD)
        mock_buzzer.assert_has_calls([call(c.BUZZER_PIN, GPIO.HIGH), call(c.BUZZER_PIN, GPIO.LOW)])

    @patch.object(DisplayManager, "update_display_info")
    @patch.object(IBS, "get_charge_left")
    def test_should_update_the_display_after_moving_forward(self, mock_ibs: Mock, display_mock: Mock):
        r = Room(2, 2)
        c = CleaningRobot(r)
        c.initialize_robot()
        mock_ibs.return_value = 12
        c.execute_command(c.FORWARD)
        display_mock.assert_called_once_with((0, 1, 'N'), None, 12)

    @patch.object(DisplayManager, "update_display_info")
    @patch.object(IBS, "get_charge_left")
    def test_should_update_the_display_after_rotating_right(self, mock_ibs: Mock, display_mock: Mock):
        r = Room(2, 2)
        c = CleaningRobot(r)
        c.initialize_robot()
        mock_ibs.return_value = 12
        c.execute_command(c.RIGHT)
        display_mock.assert_called_once_with((0, 0, 'E'), None, 12)

    @patch.object(DisplayManager, "update_display_info")
    @patch.object(IBS, "get_charge_left")
    def test_should_update_the_display_after_rotating_left(self, mock_ibs: Mock, display_mock: Mock):
        r = Room(2, 2)
        c = CleaningRobot(r)
        c.initialize_robot()
        mock_ibs.return_value = 12
        c.execute_command(c.LEFT)
        display_mock.assert_called_once_with((0, 0, 'W'), None, 12)

    @patch.object(GPIO, "input")
    @patch.object(DisplayManager, "update_display_info")
    @patch.object(IBS, "get_charge_left")
    def test_should_update_the_display_on_obstacle_found(self, mock_ibs: Mock, display_mock: Mock, mock_gpio: Mock):
        r = Room(2, 2)
        c = CleaningRobot(r)
        c.initialize_robot()
        mock_ibs.return_value = 12
        mock_gpio.return_value = True
        c.execute_command(c.FORWARD)
        display_mock.assert_called_once_with((0, 0, 'N'), (0, 1), 12)

    @patch.object(DisplayManager, "update_display_low_power")
    @patch.object(IBS, "get_charge_left")
    def test_should_update_the_display_on_low_power(self, mock_ibs: Mock, display_mock: Mock):
        r = Room(2, 2)
        c = CleaningRobot(r)
        c.initialize_robot()
        mock_ibs.return_value = 8
        c.execute_command(c.FORWARD)
        display_mock.assert_called_once()
