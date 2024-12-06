from unittest import TestCase
from unittest.mock import Mock, patch, call

from mock import GPIO
from mock.ibs import IBS
from src.cleaning_robot import CleaningRobot


class TestCleaningRobot(TestCase):

    def test_should_reset_robot_position(self):
        c = CleaningRobot()
        c.initialize_robot()
        self.assertEqual(c.robot_status(), "(0,0,N)")
