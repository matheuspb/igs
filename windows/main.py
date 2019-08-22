from gi.repository import Gtk
import numpy as np

from models.object import Object
from models.world import World
from .dialog import EntryDialog


class MainWindow:
    """
        Main window that contains the viewport to the world.

        In this class comments, the actual slice of the world that is being
        shown, is refered to as "window". The widget that shows the window is
        called "viewport", it is an immutable object. On the other hand, the
        window can be moved or scaled using the buttons.
    """

    VIEWPORT_SIZE = (500, 500)

    def __init__(self):
        # build GTK GUI using glade file
        self._builder = Gtk.Builder()
        self._builder.add_from_file("layouts/main.glade")
        handlers = {
            "on_destroy": Gtk.main_quit,
            "on_draw": self._on_draw,
            "on_button_up_clicked": lambda _: self._move_window(0, 1),
            "on_button_down_clicked": lambda _: self._move_window(0, -1),
            "on_button_left_clicked": lambda _: self._move_window(-1, 0),
            "on_button_right_clicked": lambda _: self._move_window(1, 0),
            "on_zoom_in": lambda _: self._zoom(True),
            "on_zoom_out": lambda _: self._zoom(False),
            # menu bar buttons
            "on_menu_bar_quit": Gtk.main_quit,
            "on_create_wireframe": self._create_wireframe,
        }
        self._builder.connect_signals(handlers)
        self._builder.get_object("viewport").set_size_request(
            *MainWindow.VIEWPORT_SIZE)

        # create some dummy objects
        self._world = World({
            Object([(-50, 50), (50, 50), (50, -50), (-50, -50), (-50, 50)]),
            Object([(-80, -100), (-50, -150), (-20, -100), (-80, -100)]),
        })

        # set viewport center position relative to world coordinates
        self._position = (0, 0)

        # set viewport size relative to the world
        self._window_size = MainWindow.VIEWPORT_SIZE

    def show(self):
        self._builder.get_object("main_window").show_all()

    def _viewport_transform(self):
        """
            Returns a list of lists of coordinates, ready to be drawn in the
            viewport. Basically this returns all world objects normalized to
            the viewport coordinates.
        """
        # calculate window boundaries in the world
        xw_min = self._position[0] - self._window_size[0]/2
        yw_min = self._position[1] - self._window_size[1]/2
        xw_max = self._position[0] + self._window_size[0]/2
        yw_max = self._position[1] + self._window_size[1]/2

        def transform_point(point):
            newx = ((point[0] - xw_min)/(xw_max - xw_min)) * \
                MainWindow.VIEWPORT_SIZE[0]
            newy = (1 - (point[1] - yw_min)/(yw_max - yw_min)) * \
                MainWindow.VIEWPORT_SIZE[1]
            return (newx, newy)

        # build a list of transformed points for each object
        return [
            list(map(transform_point, obj.points))
            for obj in self._world.objects]

    def _on_draw(self, _, ctx):
        ctx.set_line_width(2)
        ctx.set_source_rgb(0, 0, 0)
        for obj in self._viewport_transform():
            ctx.move_to(*obj[0])
            for point in obj[1:]:
                ctx.line_to(*point)
        ctx.stroke()

    def _move_window(self, x_offset, y_offset):
        """
            Move the window by moving its center position.
        """
        step = int(self._builder.get_object("move_step_entry").get_text())
        self._position = np.add(self._position, (x_offset*step, y_offset*step))
        self._builder.get_object("viewport").queue_draw()

    def _zoom(self, zoom_in):
        """
            Zoom in or out by scaling the window size.
        """
        step = int(self._builder.get_object("move_step_entry").get_text())
        # if zoom_in is True, reduce the window by a factor of 100 - step %
        factor = (1 - step/100)**(1 if zoom_in else -1)
        self._window_size = np.multiply(self._window_size, (factor, factor))
        self._builder.get_object("viewport").queue_draw()

    def _create_wireframe(self, _):
        dialog = EntryDialog("Enter the coordinates", "0,0;50,0;50,50")
        entry = dialog.run()
        dialog.destroy()

        if entry is not None:
            points = [
                (int(point[0]), int(point[1])) for point in
                map(lambda p: p.split(","), entry.split(";"))]

            self._world.add_object(Object(points + points[:1]))
            self._builder.get_object("viewport").queue_draw()
