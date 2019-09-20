""" This module contains a class that describes an object in the world. """
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
        """ Moves the object by an offset = (x, y). """
        for pos, point in enumerate(self._points):
            self._points[pos] = tuple(np.add(point, offset))

    def zoom(self, factor):
        """ Zooms in the object by 'factor' times. """
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

    def clip(self, window):
        boundaries = window.real_boundaries
        if len(self._points) == 2:
            self._points, _ = Object.clip_line(
                *self._points[0], *self._points[1],
                *boundaries[0], *boundaries[1])
        elif self._points[0] == self._points[-1]:
            clipped = []
            entered, exited = -1, -1
            for i in range(len(self._points) - 1):
                points, side = Object.clip_line(
                    *self._points[i], *self._points[i + 1],
                    *boundaries[0], *boundaries[1])
                if not points:
                    continue
                if side[0] > -1:  # entered
                    if exited > -1:
                        j = exited
                        while j != side[0]:
                            j = (j + 1) % 4
                            clipped.append(window.points[j])
                    else:
                        entered = side[0]
                    clipped.append(points[0])
                if side[1] > -1:  # exited
                    exited = side[1]
                    clipped.append(points[0])
                    clipped.append(points[1])
                else:
                    clipped.append(points[0])
            if clipped:
                if entered > -1:
                    j = exited
                    while j != entered:
                        j = (j + 1) % 4
                        clipped.append(window.points[j])
                clipped.append(clipped[0])
            self._points = clipped

    @staticmethod
    def clip_line(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
        """ Liang-Barsky line clipping algorithm. """
        dx, dy = x2 - x1, y2 - y1
        p = [-dx, -dy, dx, dy]
        q = [x1 - xmin, y1 - ymin, xmax - x1, ymax - y1]
        r = np.divide(q, p)
        u1, u2 = 0, 1
        side = [-1, -1]
        for i in range(4):
            if p[i] == 0 and q[i] < 0:
                return [], side
            if p[i] < 0:  # entered
                if r[i] > u1:
                    side[0] = i
                    u1 = r[i]
            if p[i] > 0:  # exited
                if r[i] < u2:
                    side[1] = i
                    u2 = r[i]
        if u1 > u2:
            return [], side
        else:
            p1 = tuple(np.add((x1, y1), (u1*dx, u1*dy)))
            p2 = tuple(np.add((x1, y1), (u2*dx, u2*dy)))
        return [p1, p2], side

    @staticmethod
    def build_from_file(path):
        """ Returns objects described in an OBJ file. """
        with open(path) as obj:
            raw_file = obj.read()
        file_lines = [line.split(" ") for line in raw_file.split("\n")]

        vertices = {}
        faces = []
        for number, line in enumerate(file_lines):
            if line[0] == "v":
                vertices[number + 1] = (int(line[1]), int(line[2]))
            if line[0] == "f":
                face = []
                for index in line[1:]:
                    face.append(vertices[int(index)])
                face.append(vertices[int(line[1])])
                faces.append(face)
        return [Object(points=face) for face in faces]


class Window(Object):
    """
        The window object.

        This object delimits what should be drawn in the viewport. Moving and
        rescaling it has the effect to change which portion of the world is
        drawn at the viewport.
    """

    BORDER = 0.05

    def __init__(self, width, height):
        points = [
            (-width/2, height/2),
            (-width/2, -height/2),
            (width/2, -height/2),
            (width/2, height/2),
        ]
        points.append(points[0])
        super().__init__(points, "window", (0, 0, 0))

    @property
    def expanded_boundaries(self):
        width = self._points[3][0] - self._points[1][0]
        height = self._points[3][1] - self._points[1][1]
        factor = np.multiply((width, height), Window.BORDER)
        return (
            np.subtract(self._points[1], factor),
            np.add(self._points[3], factor))

    @property
    def real_boundaries(self):
        """ Returns windows' bottom left and upper right coordinates. """
        return (self._points[1], self._points[3])

    @property
    def angle(self):
        """ Returns the angle of the 'view up' vector. """
        window_up = np.subtract(self._points[0], self._points[1])
        return np.arctan2(1, 0) - np.arctan2(window_up[1], window_up[0])

    def move(self, offset):
        angle = self.angle
        # rotate offset angle so movements are relative to window's angle
        offset = np.dot(offset, [
            [np.cos(angle), -np.sin(angle)],
            [np.sin(angle), np.cos(angle)],
        ])
        super().move(offset)

    def zoom(self, factor):
        # save original state
        original_points = self._points.copy()

        # apply the zoom operation
        super().zoom(factor**(-1))

        # find new window size
        minimum, maximum = self.real_boundaries
        width = np.abs(maximum[0] - minimum[0])
        height = np.abs(maximum[1] - minimum[1])

        # if zoom was exceeded, go back to original state and raise an error
        if width < 10 and height < 10:
            self._points = original_points
            raise RuntimeError("Maximum zoom in exceeded")

    def clip(self, _):
        pass
