from django.test import TestCase
from unittest import mock

from toyrobot.management.commands.run_simulator import *
from toyrobot.utils.utils import *

class TestSimulator(TestCase):
    def setUp(self):
        self.simulator = Simulator()
        util_config = ToyRobotCommandsConfigUtil()
        mock_setup = mock.patch("toyrobot.management.commands.run_simulator.Setup")
        mock_util_config = mock.patch("toyrobot.utils.utils.ToyRobotCommandsConfigUtil")
        mock_commands_executor = mock.patch("toyrobot.management.commands.run_simulator.commands_executor.execute")
        mock_display_simulation_start = \
            mock.patch("toyrobot.management.commands.run_simulator.Simulator.display_simulation_start")

        self.mock_setup = mock_setup.start()
        self.mock_setup._commands = ['PLACE 0,0,north','REPORT']
        self.mock_setup._toy_robot = mock.MagicMock()
        self.mock_setup._table = Table()
        self.mock_setup._help = mock.MagicMock()

        self.mock_util_config = mock_util_config.start()
        self.mock_util_config.return_value = util_config

        self.mock_commands_executor = mock_commands_executor.start()

        self.mock_display_simulation_start = mock_display_simulation_start.start()
        self.mock_display_simulation_start.return_value = ' '.join(self.mock_setup._commands)

        self.addCleanup(mock_setup.stop)
        self.addCleanup(mock_util_config.stop)
        self.addCleanup(mock_commands_executor.stop)
        self.addCleanup(mock_display_simulation_start.stop)

    def test_simulator_singleton(self):
        simulator = Simulator()
        self.assertEqual(self.simulator, simulator)
        self.assertEqual(self.simulator, simulator.instance())

    def test_setup_simulator(self,):
        kwargs = {'file': None}
        self.simulator.setup_simulator(**kwargs)
        self.assertEqual(len(self.simulator.instance()._setup), 2)
        self.simulator.setup_simulator(**kwargs)
        self.assertEqual(len(self.simulator.instance()._setup), 3)
        self.mock_setup.assert_called()


    def test_run_commands(self, ):
        setup = self.mock_setup
        self.simulator.run_commands(setup=setup)
        self.mock_commands_executor.assert_called()
        self.mock_display_simulation_start.assert_called_once_with(setup._commands)


    @mock.patch("toyrobot.management.commands.run_simulator.Simulator.run_commands")
    def test_run_simulator(self, mock_run_commands):
        kwargs = {'file': None}
        self.simulator.setup_simulator(**kwargs)
        mock_run_commands.return_value = self.simulator.instance()._setup[0]
        self.simulator.run_simulator()
        setup = self.simulator.instance()._setup[0]
        mock_run_commands.assert_called_once_with(setup=setup)





