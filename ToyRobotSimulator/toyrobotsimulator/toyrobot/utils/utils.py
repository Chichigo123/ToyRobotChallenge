from functools import partial, wraps
from toyrobot.sim_objects.sim_objects import Table, Position
from .conf import init_config

import re

class ToyRobotCommandsConfigUtil(object):
    # Singleton implementation of Configuration
    _instance = None

    def __new__(cls, config=None):
        if cls._instance is None:
            if cls._instance is None:
                cls._instance = super(ToyRobotCommandsConfigUtil, cls).__new__(cls)
                cls._instance.config = config or init_config
        return cls._instance

    @classmethod
    def instance(cls):
        if cls._instance is None:
            raise RuntimeError('Toy Robot Config instance not yet created')
        return cls._instance

    @classmethod
    def get_help(cls, table):
        config = cls._instance.config
        help = "The robot must be initially placed on the {} x {} table.\n\n" \
               "\tCOMMANDS\t\t\t\t\tDescription\n"\
               "{} x,y,f\t\t\t\t- where x=[0-{}), y=[0-{}), f(facing)={} e.g PLACE 0,1,EAST\n" \
               "{}\t\t\t\t\t- moves the robot one unit forward in the direction it is currently facing\n" \
               "{}\t\t\t\t- rotates the robot 90 degrees in the specified direction without changing robot's position\n"\
               "{}\t\t\t\t\t- announces the x y f of the robot\n\n" \
               "Once done giving the commands, please hit Enter to start the simulation."\
               .format(table.x, table.y, '|'.join(config.get('commands', {}).get('start', [])),
                       table.x, table.y, '|'.join(config.get('directions', [])),
                       '|'.join(config.get('commands', {}).get('movement', [])),
                       '|'.join(config.get('commands', {}).get('rotate', [])),
                       '|'.join(config.get('commands', {}).get('report', [])))
        return help

    @classmethod
    def build_regex_pattern(cls,):
        pattern = ''
        table = Table.instance()
        for command in cls.valid_commands:
            pattern += '^' + command
            if command in cls.start_command:
                pattern += ' [0-{}],[0-{}],({})'.format(table.x - 1, table.y - 1, '|'.join(cls.directions))
            pattern += '$'
            pattern += '|'
        return pattern.strip('|')

    @classmethod
    def filter_with_init_place_command(cls, commands):
        for idx, command in enumerate(commands):
            if cls.start_command[0] in command:
                commands = commands[idx:]
                return commands
        return []

    @classmethod
    def get_inputs(cls, file=None, test_commands=None):
        pattern = cls.build_regex_pattern()

        def filter_input(command):
            return command if re.match(pattern, command) else None

        if file:
            print('Toy Robot Challenge using file')
            return

        # Switch to user based input
        user_input = None
        commands = test_commands or []
        if not test_commands:
            while (user_input != ''):
                user_input = str.upper(input())
                command = filter_input(user_input.strip())
                if command:
                    commands.append(command)

        commands = cls.filter_with_init_place_command(commands)

        if not commands:
            print("No valid commands found. Please try again.")
        return commands


    @staticmethod
    def get_initial_place_command(command):
        try:
            start_command = command.split(' ')[1:][0]
            return start_command.split(',')
        except:
            raise RuntimeError("PLACE failed.")


    @classmethod
    @property
    def start_command(cls):
        return cls.instance().config.get('commands', {}).get('start', [])


    @classmethod
    @property
    def rotate(cls):
        return cls.instance().config.get('commands', {}).get('rotate', [])

    @classmethod
    @property
    def directions(cls):
        return cls.instance().config.get('directions', [])

    @classmethod
    @property
    def movemement(cls):
        return cls.instance().config.get('commands', {}).get('movement', [])

    @classmethod
    @property
    def valid_commands(cls):
        commands = cls.instance().config.get('commands', {}).values()
        return [x for y in commands for x in y]


    @staticmethod
    def is_on_edge(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            new_position = kwargs.get('new_position', None)
            table = Table.instance()

            def is_x_valid(new_x, table_x):
                return new_x >= 0 and new_x < table_x

            def is_y_valid(new_y, table_y):
                return new_y >= 0 and new_y < table_y

            is_valid = is_x_valid(new_position.x, table.x) and is_y_valid(new_position.y, table.y)
            kwargs['valid'] = is_valid
            return func(*args, **kwargs)

        return wrapper

    @staticmethod
    def get_raw_command(command):
        return command.split(' ')[0]

util_config = ToyRobotCommandsConfigUtil

class ToyRobotCommandsExecutor(object):

    @classmethod
    def execute(cls, *args, **kwargs):
        def get_command(raw_command):
            return cls.__getattribute__(cls, raw_command)
        command = kwargs.get('command', ' ')
        current_position = kwargs.get('position', None)
        directions = kwargs.get('directions', None)
        action = kwargs.get('action', None)

        if command:
            raw_command = util_config.get_raw_command(command)
            if action == 'move':
                raw_command = get_command(raw_command + '_' + current_position.f)
            else:
                raw_command = get_command(raw_command)
            if action == 'place':
                _command = partial(raw_command, command)
            else:
                _command = partial(raw_command,
                                   current_position=current_position,
                                   directions=directions)

        new_position = _command()
        return cls.return_position(current_position=current_position,
                                   new_position=new_position)

    @classmethod
    @ToyRobotCommandsConfigUtil.is_on_edge
    def return_position(cls, **kwargs):
        current_position = kwargs.get('current_position', None)
        new_position = kwargs.get('new_position', None)
        valid = kwargs.get('valid', False)
        return new_position if valid == True else current_position

    @staticmethod
    def PLACE(command):
        new_position = util_config.get_initial_place_command(command)
        return Position([new_position[0], new_position[1], new_position[2]])

    @staticmethod
    def MOVE(**kwargs):
        current_position = kwargs.get('current_position', None)
        facing = 'MOVE_' + current_position.f
        return facing(current_position)

    # @
    @staticmethod
    def MOVE_NORTH(**kwargs):
        current_position = kwargs.get('current_position', None)
        return Position([current_position.x, current_position.y + 1, current_position.f])

    # @is_on_edge
    @staticmethod
    def MOVE_SOUTH(**kwargs):
        current_position = kwargs.get('current_position', None)
        return Position([current_position.x, current_position.y - 1, current_position.f])

    # @is_on_edge
    @staticmethod
    def MOVE_EAST(**kwargs):
        current_position = kwargs.get('current_position', None)
        return Position([current_position.x + 1, current_position.y, current_position.f])

    # @is_on_edge
    @staticmethod
    def MOVE_WEST(**kwargs):
        current_position = kwargs.get('current_position', None)
        return Position([current_position.x - 1, current_position.y, current_position.f])

    @staticmethod
    def LEFT(**kwargs):
        current_position = kwargs.get('current_position', None)
        directions = kwargs.get('directions', None)
        index_of_f = directions.index(current_position.f)
        try:
            new_f = directions[index_of_f - 1]
        except:
            new_f = directions[len(directions) - 1]
        return Position([current_position.x, current_position.y, new_f])


    @staticmethod
    def RIGHT(**kwargs):
        current_position = kwargs.get('current_position', None)
        directions = kwargs.get('directions', None)
        index_of_f = directions.index(current_position.f)
        try:
            new_f = directions[index_of_f + 1]
        except:
            new_f = directions[0]
        return Position([current_position.x, current_position.y, new_f])

    @staticmethod
    def REPORT(**kwargs):
        current_position = kwargs.get('current_position', None)
        if current_position:
            print("[REPORT] TOY ROBOT POSITION: {} {} {}".format(current_position.x, current_position.y, current_position.f))
            return Position([current_position.x, current_position.y, current_position.f])
        raise RuntimeError("Invalid Report issued.")