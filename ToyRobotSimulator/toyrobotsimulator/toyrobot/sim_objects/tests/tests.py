from django.test import TestCase
from unittest import mock

from toyrobot.sim_objects.sim_objects import *


class TestSimObjects(TestCase):
    def setUp(self):
        self.table = Table()

    def test_table_singleton(self):
        table = Table()
        self.assertEqual(self.table, table)
        self.assertEqual(self.table, table.instance())


    def test_table_size_still_5_5(self):
        table = Table(3, 3)
        self.assertEqual(self.table, table)
        self.assertEqual(self.table.x, 5)
        self.assertEqual(self.table.y, 5)


    def test_position(self):
        xyf = [3,3,'NORTH']
        position = Position(xyf)
        self.assertEqual(position.x, xyf[0])
        self.assertEqual(position.y, xyf[1])
        self.assertEqual(position.f, xyf[2])


    def test_toy_robot(self):
        xyf = [4, 4, 'WEST']
        position = Position(xyf)
        toy_robot = ToyRobot(xyf)
        self.assertEqual(toy_robot._position.x, position.x)
        self.assertEqual(toy_robot._position.y, position.y)
        self.assertEqual(toy_robot._position.f, position.f)