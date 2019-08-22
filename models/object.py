class Object:

    TOTAL_OBJECTS = 0

    def __init__(self, points=None, name=None):
        self._points = [] if points is None else points
        self._name = self.default_name() if name is None else name
        Object.TOTAL_OBJECTS += 1

    @property
    def points(self):
        return self._points

    @property
    def name(self):
        return self._name

    @staticmethod
    def default_name():
        return "object{}".format(Object.TOTAL_OBJECTS + 1)
