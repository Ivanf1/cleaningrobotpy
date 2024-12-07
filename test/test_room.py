from unittest import TestCase

from src.room import Room


class TestRoom(TestCase):

    def test_should_return_position_valid(self):
        r = Room(2, 2)
        self.assertTrue(r.is_position_valid((1, 1)))
