""" This module contains a class that describes an object in the world """
import numpy as np


class Object:
    """
        Object is a simple wireframe composed of multiple points connected by
        lines that can be drawn in the viewport.
    """

    TOTAL_OBJECTS = 0

    def __init__(self, points=None, name=None):
        self._points = [] if points is None else points
        self._name = self.default_name() if name is None else name
        Object.TOTAL_OBJECTS += 1

    @staticmethod
    def default_name():
        """ Default name for new objects. """
        return "object{}".format(Object.TOTAL_OBJECTS + 1)

    @property
    def points(self):
        """ The points in the wireframe. """
        return self._points

    @property
    def name(self):
        """ Name of the object. """
        return self._name

    def move(self, offset):
        for pos, point in enumerate(self._points):
            self._points[pos] = tuple(np.add(point, offset))

    def zoom(self, factor):
        x_points = [point[0] for point in set(self._points)]
        y_points = [point[1] for point in set(self._points)]
        center = (np.average(x_points), np.average(y_points))
        print(center)
        for pos, point in enumerate(self._points):
            new_point = np.subtract(point, center)
            new_point = np.multiply(new_point, (factor, factor))
            self._points[pos] = tuple(np.add(new_point, center))
