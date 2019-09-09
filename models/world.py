""" This module contains the World class. """
from models.object import Window


class World:
    """
        Contains all objects that are supposed to be drawn in the viewport.

        In this class comments, the actual slice of the world that is being
        shown, is refered to as "window". The widget that shows the window is
        called "viewport", it is an immutable object. On the other hand, the
        window can be moved or scaled like any other object.
    """

    def __init__(self, window_size):
        self._objects = dict()
        self.add_object(Window(*window_size))

    def __getitem__(self, name):
        return self._objects[name]

    def viewport_transform(self, viewport_width, viewport_height):
        """
            Returns a list of lists of coordinates, ready to be drawn in the
            viewport. Basically this returns all world objects normalized to
            the viewport coordinates.
        """
        (x_min, y_min), (x_max, y_max) = self["window"].boundaries

        def transform_point(point):
            newx = ((point[0] - x_min)/(x_max - x_min)) * viewport_width
            newy = (1 - (point[1] - y_min)/(y_max - y_min)) * viewport_height
            return (newx, newy)

        # build a list of transformed points for each object
        return [list(map(transform_point, obj.points)) for obj in self.objects]

    @property
    def objects(self):
        """ Returns the set of objects. """
        return self._objects.values()

    def add_object(self, obj):
        """ Adds a new object. """
        self._objects[obj.name] = obj
