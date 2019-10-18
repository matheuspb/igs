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
        points = set()
        for face in self._points:
            points.update(face)
        x_points = [point[0] for point in points]
        y_points = [point[1] for point in points]
        z_points = [point[2] for point in points]
        return \
            (np.average(x_points), np.average(y_points), np.average(z_points))

    def _transform(self, matrix, center=None, offset=None):
        center = self.center if center is None else center

        # move object to center
        operation_matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [-center[0], -center[1], -center[2], 1],
        ])

        # perform operation
        operation_matrix = operation_matrix.dot([
            matrix[0] + [0],
            matrix[1] + [0],
            matrix[2] + [0],
            ([0, 0, 0] if offset is None else offset) + [1],
        ])

        # move object back to original position
        operation_matrix = operation_matrix.dot([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [center[0], center[1], center[2], 1],
        ])

        for fpos, face in enumerate(self._points):
            for ppos, point in enumerate(face):
                new_point = np.dot(point + (1,), operation_matrix)
                self._points[fpos][ppos] = tuple(new_point[:3])

    def move(self, offset):
        """ Moves the object by an offset = (x, y). """
        self._transform(
            [
                [1, 0, 0],
                [0, 1, 0],
                [0, 0, 1],
            ], center=None, offset=list(offset))

    def zoom(self, factor):
        """ Zooms in the object by 'factor' times. """
        self._transform(
            [
                [factor, 0, 0],
                [0, factor, 0],
                [0, 0, factor],
            ])

    @staticmethod
    def generate_rotation_matrix(x_angle, y_angle, z_angle):
        """ Generates the matrix that rotates points. """
        return np.array([
            [1, 0, 0],
            [0, np.cos(x_angle), -np.sin(x_angle)],
            [0, np.sin(x_angle), np.cos(x_angle)],
        ]).dot([
            [np.cos(y_angle), 0, np.sin(y_angle)],
            [0, 1, 0],
            [-np.sin(y_angle), 0, np.cos(y_angle)],
        ]).dot([
            [np.cos(z_angle), -np.sin(z_angle), 0],
            [np.sin(z_angle), np.cos(z_angle), 0],
            [0, 0, 1],
        ]).tolist()

    def rotate(self, x_angle, y_angle, z_angle, center=None):
        """ Rotates the object around center, the angle is in radians. """
        self._transform(
            Object.generate_rotation_matrix(x_angle, y_angle, z_angle),
            center)

    def project(self):
        """ Projects the 3D objects to 2D. Using parallel projection. """
        self._points = [[point[:2] for point in face] for face in self._points]

    def clip(self, window):
        """ Weiler-Atherton polygon clipping algorithm. """

        def connect_points(clipped, side1, side2, window):
            """ Connects points of the window. """
            edge = side1
            while edge != side2:
                clipped.append(window.points[0][edge])
                edge = (edge - 1) % 4

        boundaries = window.real_boundaries
        clipped = []
        for face in self._points:
            new_face = []
            entered, exited = None, None
            for i in range(len(face) - 1):
                points, side = Object._clip_line(
                    face[i], face[i + 1], *boundaries[0], *boundaries[1])

                if not points:  # clipped line is outside window
                    continue

                if side[0] is not None:  # entered
                    if exited is not None:
                        connect_points(new_face, exited, side[0], window)
                    else:
                        entered = side[0]

                if side[1] is not None:  # exited
                    exited = side[1]
                    new_face.append(points[0])
                    new_face.append(points[1])
                else:
                    new_face.append(points[0])

            if new_face and face[0] == face[-1]:
                if entered is not None:
                    connect_points(new_face, exited, entered, window)
                new_face.append(new_face[0])

            clipped.append(new_face)

        self._points = clipped

    @staticmethod
    def _clip_line(point1, point2, xmin, ymin, xmax, ymax):
        """ Liang-Barsky line clipping algorithm. """
        deltax, deltay = point2[0] - point1[0], point2[1] - point1[1]
        deltas = [-deltax, -deltay, deltax, deltay]  # p
        distances = [  # q
            point1[0] - xmin, point1[1] - ymin,
            xmax - point1[0], ymax - point1[1]]
        ratios = np.divide(distances, deltas)  # r
        pct1, pct2 = 0, 1  # how much of the line is inside the window
        side = [None, None]
        for i in range(4):
            if deltas[i] == 0 and distances[i] < 0:
                return (), side
            if deltas[i] < 0:
                if ratios[i] > pct1:  # entered
                    side[0] = i
                    pct1 = ratios[i]
            if deltas[i] > 0:
                if ratios[i] < pct2:  # exited
                    side[1] = i
                    pct2 = ratios[i]
        if pct1 > pct2:
            return (), side
        clipped = (
            tuple(np.add((point1[0], point1[1]), (pct1*deltax, pct1*deltay))),
            tuple(np.add((point1[0], point1[1]), (pct2*deltax, pct2*deltay))),
        )
        return clipped, side

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
                vertices[number + 1] = tuple(map(float, line[1:]))
            if line[0] == "f":
                face = []
                for index in line[1:]:
                    face.append(vertices[int(index)])
                face.append(vertices[int(line[1])])
                faces.append(face)
        return Object(points=faces)


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
            (-width/2, height/2, 0),
            (-width/2, -height/2, 0),
            (width/2, -height/2, 0),
            (width/2, height/2, 0),
        ]
        points.append(points[0])
        super().__init__([points], "window", (0, 0, 0))
        self._angles = np.array([0, 0, 0])

    @property
    def expanded_boundaries(self):
        """ Boundaries a little bigger than the actual window. """
        width = self._points[0][3][0] - self._points[0][1][0]
        height = self._points[0][3][1] - self._points[0][1][1]
        factor = np.multiply((width, height), Window.BORDER)
        return (
            np.subtract(self._points[0][1], factor),
            np.add(self._points[0][3], factor))

    @property
    def real_boundaries(self):
        """ Returns windows' bottom left and upper right coordinates. """
        return (self._points[0][1], self._points[0][3])

    @property
    def angles(self):
        """ Returns how much the window is rotated. """
        return self._angles

    def move(self, offset):
        # rotate offset vector to move window relative to its own directions
        offset = np.dot(offset, Object.generate_rotation_matrix(*self.angles))
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

    def rotate(self, x_angle, y_angle, z_angle, center=None):
        # update _angles variable for later
        self._angles = np.add(self._angles, [x_angle, y_angle, z_angle])
        super().rotate(x_angle, y_angle, z_angle, center)

    def clip(self, _):
        pass


class Curve(Object):
    """ A Bezier curve with four control points. """

    def __init__(self, points, name=None, color=None):
        curve = Curve._generate_curve(points)
        curve.append(points[-1])  # add stub point for clipping
        super().__init__(
            points=curve, name=name, color=color)

    @staticmethod
    def _generate_curve(points):
        def f(t, i):
            return np.array([t**3, t**2, t, 1]).dot(np.array([
                [-1, 3, -3, 1],
                [3, -6, 3, 0],
                [-3, 3, 0, 0],
                [1, 0, 0, 0],
            ])).dot(np.array([p[i] for p in points]))

        step = 0.02
        x_points = [f(t, 0) for t in np.arange(0, 1+step, step)]
        y_points = [f(t, 1) for t in np.arange(0, 1+step, step)]

        return list(zip(x_points, y_points))


class Spline(Object):
    """ A Spline curve with arbitrary amount of control points. """

    def __init__(self, points, name=None, color=None):
        curve = []
        for i in range(len(points) - 3):
            # build a curve for every four control points
            curve += Spline._generate_curve(points[i:i+4])
        super().__init__(
            points=curve, name=name, color=color)

    @staticmethod
    def _generate_curve(points):
        coef = np.multiply(1/6, np.array([
            [-1, 3, -3, 1],
            [3, -6, 3, 0],
            [-3, 0, 3, 0],
            [1, 4, 1, 0],
        ])).dot(np.array(points))

        number_of_points = 50
        delta = 1/number_of_points
        deltas = np.array([
            [0, 0, 0, 1],
            [delta**3, delta**2, delta, 0],
            [6*delta**3, 2*delta**2, 0, 0],
            [6*delta**3, 0, 0, 0],
        ]).dot(coef)

        points = [tuple(deltas[0])]
        for _ in range(number_of_points):
            # update coordinates using forward differences
            deltas[0] += deltas[1]
            deltas[1] += deltas[2]
            deltas[2] += deltas[3]
            points.append(tuple(deltas[0]))

        return points
