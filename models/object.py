class Object:

    def __init__(self, points=None):
        self._points = [] if points is None else points

    @property
    def points(self):
        return self._points
