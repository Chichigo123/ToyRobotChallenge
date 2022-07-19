from toyrobot.utils.conf import init_config

class Table(object):
    # Singleton implementation of Table, to sim_objects multiple robots that will be placed in the table
    _instance = None

    def __new__(cls, x=None, y=None):
        if cls._instance is None:
            if cls._instance is None:
                cls._instance = super(Table, cls).__new__(cls)
                cls._instance.x = x or init_config.get('table')[0]
                cls._instance.y = y or init_config.get('table')[1]
        return cls._instance

    @classmethod
    def instance(cls):
        if cls._instance is None:
            raise RuntimeError('Table instance not yet created')
        return cls._instance


class Position(object):
    x, y, f = None, None, None

    def __init__(self, position):
        self.x, self.y, self.f = int(position[0]), int(position[1]), position[2]


class ToyRobot(object):
    _position = None

    def __init__(self, position):
        if not(isinstance(position, list)) or position is None:
            raise RuntimeError("Please provide toy robot's initial position")
        self._position = Position(position)

    def _set_new_position(self, position):
        self._position = position
