from django.test import TestCase
from unittest import mock

from toyrobot.utils.utils import *
from toyrobot.sim_objects.sim_objects import Table, Position


class TestToyRobotCommandsConfigUtil(TestCase):
    def setUp(self):
        self.table = Table()
        self.util_config = ToyRobotCommandsConfigUtil()
        self._commands = ["PLACE 0,1,NORTH", "MOVE", 'MOVE',
                          "MEOV", "PLACE 4,5,", "REPORT"]

    def test_util_config_singleton(self):
        util_config = ToyRobotCommandsConfigUtil()
        self.assertEqual(self.util_config, util_config)
        self.assertEqual(self.util_config, util_config.instance())

    def test_build_regex_pattern(self):
        pattern = self.util_config.build_regex_pattern()
        self.assertEqual(pattern, '^PLACE [0-4],[0-4],(NORTH|EAST|SOUTH|WEST)$|^MOVE$|^LEFT$|^RIGHT$|^REPORT$')

    @mock.patch("toyrobot.utils.utils.ToyRobotCommandsConfigUtil.filter_with_init_place_command")
    def test_get_inputs(self, mock_filter_with_init_place_command):
        mock_filter_with_init_place_command.return_value = ['PLACE 0,1,NORTH', 'MOVE', 'MOVE', 'REPORT']
        commands = self.util_config.get_inputs(test_commands=self._commands)
        self.assertEqual(commands, ["PLACE 0,1,NORTH", "MOVE", 'MOVE', "REPORT"])


    def test_filter_with_init_place_command(self, ):
        place_in_between_commands = ["MOVE", "RIGHT", "PLACE 0,1,NORTH", "MOVE", 'MOVE',
                                     "REPORT"]
        commands = self.util_config.filter_with_init_place_command(place_in_between_commands)
        self.assertEqual(commands, ["PLACE 0,1,NORTH", "MOVE", 'MOVE', "REPORT"])


    def test_get_initial_place_command(self, ):
        valid_commands = ["PLACE 0,1,NORTH", "MOVE", 'MOVE', "REPORT"]
        position = self.util_config.get_initial_place_command(valid_commands[0])
        self.assertEqual(position, ['0', '1', 'NORTH'])


    def test_get_raw_command(self, ):
        command = "PLACE 4,4,EAST"
        raw_command = self.util_config.get_raw_command(command)
        self.assertEqual(raw_command, "PLACE")


class TestToyRobotCommandsExecutor(TestCase):
    def setUp(self):
        self.table = Table()
        self.util_config = ToyRobotCommandsConfigUtil()
        self._commands = ["PLACE 3,3,WEST", "MOVE", "LEFT", "REPORT",
                          "MOVE", "REPORT", "REPORT", "MOVE",  "RIGHT",
                          "REPORT", "MOVE", "PLACE 2,2,SOUTH", "REPORT"]
        self.commands_executor = ToyRobotCommandsExecutor()


    def run_commands(self, current_position, command):
        raw_command = self.util_config.get_raw_command(command)
        is_rotate = 'rotate' if raw_command in self.util_config.rotate else None
        is_move = 'move' if raw_command in self.util_config.movemement else None
        is_place = 'place' if raw_command in self.util_config.start_command else None

        new_position = \
            self.commands_executor.execute(command=command, action=is_rotate or is_move or is_place,
                                           position=current_position, directions=self.util_config.directions)

        return new_position

    def test_execute_stop_fall_on_table(self, ):
        test_position = [[3, 3, "WEST"], [2, 3, "WEST"], [2, 3, "SOUTH"], [2, 3, "SOUTH"],
                         [2, 2, "SOUTH"], [2, 2, "SOUTH"], [2, 2, "SOUTH"], [2, 1, "SOUTH"], [2, 1, "WEST"],
                         [2, 1, "WEST"], [1, 1, "WEST"], [2, 2, "SOUTH"],  [2, 2, "SOUTH"]]


        current_position = Position(['3', '3', 'WEST'])
        for idx, command in enumerate(self._commands):
            new_position = self.run_commands(current_position, command)

            self.assertEqual(new_position.x, test_position[idx][0])
            self.assertEqual(new_position.y, test_position[idx][1])
            self.assertEqual(new_position.f, test_position[idx][2])

            current_position = new_position


    def test_execute_on_table(self, ):
        commands = ["PLACE 0,1,NORTH", "MOVE", "RIGHT", "REPORT",
                    "MOVE", "RIGHT", "RIGHT", "MOVE",  "REPORT",
                    "LEFT", "LEFT", "LEFT", "MOVE", "REPORT"]
        test_position = [[0, 1, "NORTH"], [0, 2, "NORTH"], [0, 2, "EAST"], [0, 2, "EAST"],
                         [1, 2, "EAST"], [1, 2, "SOUTH"], [1, 2, "WEST"], [0, 2, "WEST"], [0, 2, "WEST"],
                         [0, 2, "SOUTH"], [0, 2, "EAST"], [0, 2, "NORTH"],
                         [0, 3, "NORTH"], [0, 3, "NORTH"]]


        current_position = Position(['0', '1', 'NORTH'])
        for idx, command in enumerate(commands):
            new_position = self.run_commands(current_position, command)
            self.assertEqual(new_position.x, test_position[idx][0])
            self.assertEqual(new_position.y, test_position[idx][1])
            self.assertEqual(new_position.f, test_position[idx][2])

            current_position = new_position


