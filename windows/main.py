""" This module contains the main window of the application. """
from gi.repository import Gtk
import numpy as np

from models.object import Object
from models.world import World
from .dialog import EntryDialog


class MainWindow:
    """ Main window that contains the viewport to the world. """

    VIEWPORT_SIZE = (500, 500)

    class _Decorators:
        @staticmethod
        def needs_redraw(func):
            """ Decorates methods that need to redraw to take effect. """
            def wrapper(self, *args, **kwargs):
                func(self, *args, **kwargs)
                self._builder.get_object("viewport").queue_draw()
            return wrapper

    def __init__(self):
        # build GTK GUI using glade file
        self._builder = Gtk.Builder()
        self._builder.add_from_file("layouts/main.glade")
        handlers = {
            "on_destroy": Gtk.main_quit,
            "on_draw": self._on_draw,
            "on_button_up_clicked": lambda _: self._move_object(0, 1),
            "on_button_down_clicked": lambda _: self._move_object(0, -1),
            "on_button_left_clicked": lambda _: self._move_object(-1, 0),
            "on_button_right_clicked": lambda _: self._move_object(1, 0),
            "on_zoom_in": lambda _: self._zoom_object(zoom_in=True),
            "on_zoom_out": lambda _: self._zoom_object(zoom_in=False),
            "on_button_rotate_right_clicked":
                lambda _: self._rotate_object(right=True),
            "on_button_rotate_left_clicked":
                lambda _: self._rotate_object(right=False),
            # menu bar buttons
            "on_menu_bar_quit": Gtk.main_quit,
            "on_create_wireframe": self._create_wireframe,
        }
        self._builder.connect_signals(handlers)
        self._builder.get_object("viewport").set_size_request(
            *MainWindow.VIEWPORT_SIZE)

        # create some dummy objects
        self._world = World(MainWindow.VIEWPORT_SIZE)
        self._world.add_object(
            Object([(-50, 50), (50, 50), (50, -50), (-50, -50), (-50, 50)]))
        self._world.add_object(
            Object([(-80, -100), (-50, -150), (-20, -100), (-80, -100)]))

        # create tree view that shows object names
        self._store = Gtk.ListStore(str)
        self._builder.get_object("object_tree").set_model(self._store)
        self._builder.get_object("object_tree").append_column(
            Gtk.TreeViewColumn("Name", Gtk.CellRendererText(), text=0))

        # add object names to tree view
        for obj in self._world.objects:
            self._store.append([obj.name])

    def show(self):
        """ Shows all window widgets. """
        self._builder.get_object("main_window").show_all()

    def _on_draw(self, _, ctx):
        ctx.set_line_width(2)
        ctx.set_source_rgb(0, 0, 0)
        for obj in self._world.viewport_transform(*MainWindow.VIEWPORT_SIZE):
            ctx.move_to(*obj[0])
            for point in obj[1:]:
                ctx.line_to(*point)
        ctx.stroke()

    def _get_selected(self):
        tree, pos = self._builder.get_object("object_tree") \
            .get_selection().get_selected()
        return "window" if pos is None else tree[pos][0]

    @_Decorators.needs_redraw
    def _move_object(self, x_offset, y_offset):
        """ Moves a selected object. """
        step = int(self._builder.get_object("move_step_entry").get_text())
        offset = (x_offset*step, y_offset*step)
        self._world[self._get_selected()].move(offset)

    @_Decorators.needs_redraw
    def _zoom_object(self, zoom_in):
        """ Zoom in or out the selected object. """
        step = int(self._builder.get_object("move_step_entry").get_text())
        factor = (1 + step/100)**(1 if zoom_in else -1)
        try:
            self._world[self._get_selected()].zoom(factor)
        except RuntimeError as error:
            dialog = Gtk.MessageDialog(
                self._builder.get_object("main_window"),
                Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING,
                Gtk.ButtonsType.OK, str(error))
            dialog.run()
            dialog.destroy()

    @_Decorators.needs_redraw
    def _rotate_object(self, right):
        """ Rotates the selected object left or right. """
        angle = np.radians(
            int(self._builder.get_object("angle_entry").get_text()))
        self._world[self._get_selected()].rotate(angle if right else -angle)

    @_Decorators.needs_redraw
    def _create_wireframe(self, _):
        """
            Prompts the user for a list of coordinates and builds the wireframe
            object on those points.
        """
        dialog = EntryDialog(
            self._builder.get_object("main_window"), "Enter the coordinates",
            Object.default_name(), "0,0;50,0;50,50")
        if dialog.run():
            points = dialog.points
            if dialog.wrap:
                points.append(points[0])
            self._world.add_object(Object(points, dialog.name))
            self._store.append([dialog.name])
        dialog.destroy()
