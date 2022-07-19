from django.core.management.base import BaseCommand
from functools import wraps
from toyrobot.utils.utils import ToyRobotCommandsConfigUtil, ToyRobotCommandsExecutor
from toyrobot.sim_objects.sim_objects import Position, Table, ToyRobot

commands_executor = ToyRobotCommandsExecutor()

class Setup(object):
    _table = None
    _help = None
    _toy_robot = None
    _commands = None

    def __init__(self, **kwargs):
        self._setup_table(**kwargs)
        config_util = ToyRobotCommandsConfigUtil(kwargs.pop('config', None))
        if config_util:
            self._setup_help_and_display(config_util, **kwargs)
            self._setup_commands(config_util, **kwargs)
            self._setup_toy_robot(config_util, **kwargs)


    def _setup_table(self, *args, **kwargs):
        self._table = kwargs.pop('table', None) or Table()

    def _setup_help_and_display(self, config_util, **kwargs):
        self._help = kwargs.pop('help', None) or config_util.get_help(self._table)
        self._display_help()

    def _setup_toy_robot(self, config_util, **kwargs):
        initial_place_position = config_util.get_initial_place_command(self._commands[0])
        try:
            self._toy_robot = ToyRobot(kwargs.pop('position', None) or initial_place_position)
        except:
            raise RuntimeError("Failed to create Toy Robot. No initial position found.")

    def _setup_commands(self, config_util, **kwargs):
        while not self._commands:
            self._commands = kwargs.pop('commands', None) \
                             or config_util.get_inputs(file=kwargs.get('file', None),
                                                       test_commands=kwargs.get('test_commands', None))

    def _setup_new_toy_robot_position(self, new_position):
        self._toy_robot._set_new_position(new_position)

    def _display_help(self):
        print(self._help)

class Simulator(object):
    # Singleton implementation of Simulator, to be able to create multiple sim_objects running on the simulator
    _instance = None

    def __new__(cls, ):
        if cls._instance is None:
            if cls._instance is None:
                cls._instance = super(Simulator, cls).__new__(cls)
                cls._instance._setup = []
        return cls._instance

    @classmethod
    def instance(cls):
        if cls._instance is None:
            raise RuntimeError('Simulator instance not yet created')
        return cls._instance

    def is_robot_placed_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            setup = kwargs.get('setup', None)
            if setup._toy_robot._position:
                result = func(*args, **kwargs)
                return result
            raise RuntimeError('Toy robot not yet placed')
        return wrapper

    @staticmethod
    def display_simulation_start(commands):
        print('Starting simulation. Executing commands {}'.format(commands))


    @classmethod
    @is_robot_placed_decorator
    def run_commands(cls, setup):
        commands, toy_robot = setup._commands, setup._toy_robot
        util_config = ToyRobotCommandsConfigUtil.instance()
        cls.display_simulation_start(commands)

        for command in commands:
            current_position = toy_robot._position
            raw_command = util_config.get_raw_command(command)
            is_rotate = 'rotate' if raw_command in util_config.rotate else None
            is_move = 'move' if raw_command in util_config.movemement else None
            is_place = 'place' if raw_command in util_config.start_command else None

            new_position = commands_executor.execute(
                            command=command, action=is_rotate or is_move or is_place,
                            position=current_position, directions=util_config.directions)

            toy_robot._position = new_position

        return setup

    @classmethod
    def run_simulator(cls, ):
        updated_setup = []
        for idx, setup in enumerate(cls.instance()._setup):
            updated_setup.append(cls.run_commands(setup=setup))
        cls.update(updated_setup)
        return cls


    @classmethod
    def setup_simulator(cls, **kwargs):
        cls.instance()._setup.append(Setup(**kwargs))
        return cls


    @classmethod
    def update(cls, updated_setup):
        cls.instance()._setup = updated_setup


class Command(BaseCommand):

    help = "Toy Robot Challenge"

    def add_arguments(self, parser):
        # Positional arguments

        # Named (optional) arguments
        parser.add_argument(
            '-f', '--file',
            help='Use input file to run the simulator',
            type=str
        )

        parser.add_argument(
            '-n', '--num_toy_robots',
            help='Number of toy robots in the simulator',
            type=int,
            default=1
        )


    def get_arguments(self, **options):
        num_toy_robots = options.get('num_toy_robots', 1)
        file = options.get('file', None)
        return num_toy_robots, file


    def handle(self, *args, **options):
        num_toy_robots, file = self.get_arguments(**options)
        simulator = Simulator()
        for i in range(num_toy_robots):
            simulator.setup_simulator(file=file)
        simulator.run_simulator()
