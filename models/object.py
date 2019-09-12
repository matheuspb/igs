""" This module contains a class that describes an object in the world """
import numpy as np


class Object:
    """
        Object is a simple wireframe composed of multiple points connected by
        lines that can be drawn in the viewport.
    """

    TOTAL_OBJECTS = -1

    def __init__(self, points=None, name=None, color=None):
        self._points = [] if points is None else points
        self._name = self.default_name() if name is None else name
        self._color = (0, 0, 0) if color is None else color
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

    @property
    def color(self):
        """ Color of the object. """
        return self._color

    @property
    def center(self):
        """ Center of the object. """
        x_points = [point[0] for point in set(self._points)]
        y_points = [point[1] for point in set(self._points)]
        return (np.average(x_points), np.average(y_points))

    def _transform(self, matrix, center=None):
        center = self.center if center is None else center

        # move object to center
        operation_matrix = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [-center[0], -center[1], 1],
        ])

        # perform operation
        operation_matrix = operation_matrix.dot([
            matrix[0] + [0],
            matrix[1] + [0],
            [0, 0, 1],
        ])

        # move object back to original position
        operation_matrix = operation_matrix.dot([
            [1, 0, 0],
            [0, 1, 0],
            [center[0], center[1], 1],
        ])

        for pos, point in enumerate(self._points):
            new_point = np.dot(point + (1,), operation_matrix)
            self._points[pos] = tuple(new_point[:2])

    def move(self, offset):
        """ Moves the object by an offset = (x, y) """
        for pos, point in enumerate(self._points):
            self._points[pos] = tuple(np.add(point, offset))

    def zoom(self, factor):
        """ Zooms in the object by 'factor' times """
        self._transform(
            [
                [factor, 0],
                [0, factor],
            ])

    def rotate(self, angle, center=None):
        """ Rotates the object around center, the angle is in radians. """
        self._transform(
            [
                [np.cos(angle), -np.sin(angle)],
                [np.sin(angle), np.cos(angle)],
            ], center)


class Window(Object):
    """
        The window object.

        This object delimits what should be drawn in the viewport. Moving and
        rescaling it has the effect to change which portion of the world is
        drawn at the viewport.
    """

    def __init__(self, width, height):
        points = [
            (-width/2, height/2),
            (width/2, height/2),
            (width/2, -height/2),
            (-width/2, -height/2),
        ]
        points.append(points[0])
        super().__init__(points, "window")

    @property
    def boundaries(self):
        """ Returns windows' bottom left and upper right coordinates """
        return (self._points[3], self._points[1])

    @property
    def points(self):
        return [(0, 0)]  # window shouldn't be drawn

    def zoom(self, factor):
        # save original state
        original_points = self._points.copy()

        # apply the zoom operation
        super().zoom(factor**(-1))

        # find new window size
        minimum, maximum = self.boundaries
        width = maximum[0] - minimum[0]
        height = maximum[1] - minimum[1]

        # if zoom was exceeded, go back to original state and raise an error
        if width < 10 or height < 10:
            self._points = original_points
            raise RuntimeError("Maximum zoom in exceeded")

    def rotate(self, *args):
        # not implemented yet
        pass
