""" This module contains a dialog to prompt for user input. """
import re
from gi.repository import Gtk


class EntryDialog(Gtk.MessageDialog):
    """ Prompts the user for a list of points that describe a wireframe. """

    POINTS_PATTERN = re.compile(r"^(-?\d+,-?\d+,-?\d+;)*-?\d+,-?\d+,-?\d+$")
    PADDING = 10

    class _Decorators:
        @staticmethod
        def warning(func):
            """ Opens a dialog if the inner function raises a RuntimeError. """
            def wrapper(self):
                while True:
                    try:
                        return func(self)
                    except RuntimeError as error:
                        dialog = Gtk.MessageDialog(
                            self, Gtk.DialogFlags.MODAL,
                            Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, error)
                        dialog.run()
                        dialog.destroy()
            return wrapper

    def __init__(self, parent, text, name_hint, points_hint):
        super(EntryDialog, self).__init__(
            parent, 0, Gtk.MessageType.QUESTION, (
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OK, Gtk.ResponseType.OK), text)

        # build object name entry widget
        self._name_entry = Gtk.Entry()
        self._name_entry.set_text(name_hint)
        self.vbox.pack_start(self._name_entry, False, False, 0)

        # build points entry widget
        self._points_entry = Gtk.Entry()
        self._points_entry.set_text(points_hint)
        self.vbox.pack_start(self._points_entry, False, False, 0)

        # build RGB entry
        hbox = Gtk.HBox()
        self.vbox.pack_start(hbox, False, False, 0)
        # red
        hbox.pack_start(Gtk.Label("R:"), False, False, EntryDialog.PADDING)
        self._red_entry = Gtk.Entry()
        self._red_entry.set_text("0")
        hbox.pack_start(self._red_entry, False, False, EntryDialog.PADDING)
        # green
        hbox.pack_start(Gtk.Label("G:"), False, False, EntryDialog.PADDING)
        self._green_entry = Gtk.Entry()
        self._green_entry.set_text("0")
        hbox.pack_start(self._green_entry, False, False, EntryDialog.PADDING)
        # blue
        hbox.pack_start(Gtk.Label("B:"), False, False, EntryDialog.PADDING)
        self._blue_entry = Gtk.Entry()
        self._blue_entry.set_text("0")
        hbox.pack_start(self._blue_entry, False, False, EntryDialog.PADDING)

        # show widgets inside vbox
        self.vbox.show_all()

    @_Decorators.warning
    def run(self):
        """ Runs the dialog. """
        result = super(EntryDialog, self).run()
        if result == Gtk.ResponseType.OK:
            text = self._points_entry.get_text()
            if not EntryDialog.POINTS_PATTERN.match(text):
                raise RuntimeError("Invalid points format")
            return True
        return False

    @property
    def name(self):
        """ Name of the object. """
        return self._name_entry.get_text()

    @property
    def points(self):
        """ Points of the wireframe. """
        points = list(map(
            lambda p: p.split(","), self._points_entry.get_text().split(";")))
        return [tuple(map(int, point)) for point in points]

    @property
    def color(self):
        """ Triple with the RGB color of the wireframe. """
        red = int(self._red_entry.get_text()) / 255
        green = int(self._green_entry.get_text()) / 255
        blue = int(self._blue_entry.get_text()) / 255
        return red, green, blue
