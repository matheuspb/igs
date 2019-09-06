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
            self._points[pos] = np.add(point, offset)
