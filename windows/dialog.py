""" This module contains a dialog to prompt for user input. """
import re
from gi.repository import Gtk


class EntryDialog(Gtk.MessageDialog):
    """ Prompts the user for a list of points that describe a wireframe. """

    POINTS_PATTERN = re.compile(r"^(-?\d+,-?\d+;)*-?\d+,-?\d+$")

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

        # build the wrap object check box
        self._check = Gtk.CheckButton("Connect last point to the first one")
        self._check.set_active(True)
        self.vbox.pack_start(self._check, False, False, 0)

        # set size and show widgets inside vbox
        self.set_size_request(400, 0)
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
        points = map(
            lambda p: p.split(","), self._points_entry.get_text().split(";"))
        return [(int(point[0]), int(point[1])) for point in points]

    @property
    def wrap(self):
        """ Wrap last point to the first one or not. """
        return self._check.get_active()
