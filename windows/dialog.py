import re
from gi.repository import Gtk


class EntryDialog(Gtk.MessageDialog):

    COORDINATES_PATTERN = re.compile(r"(-?\d+,-?\d+;)*-?\d+,-?\d+")

    def __init__(self, parent, text, name_hint, coordinates_hint):
        super(EntryDialog, self).__init__(
            parent, 0, Gtk.MessageType.QUESTION, (
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OK, Gtk.ResponseType.OK), text)

        # build object name entry widget
        self._name_entry = Gtk.Entry()
        self._name_entry.set_text(name_hint)
        self.vbox.pack_start(self._name_entry, False, False, 0)

        # build coordinates entry widget
        self._coordinates_entry = Gtk.Entry()
        self._coordinates_entry.set_text(coordinates_hint)
        self.vbox.pack_start(self._coordinates_entry, False, False, 0)

        # build the wrap object check box
        self._check = Gtk.CheckButton("Connect last point to the first one")
        self._check.set_active(True)
        self.vbox.pack_start(self._check, False, False, 0)

        # set size and show widgets inside vbox
        self.set_size_request(400, 0)
        self.vbox.show_all()

    def _warning(message):
        """ Raises a dialog while the inner functions raises a RuntimeError """
        def decorator(func):
            def wrapper(self):
                while True:
                    try:
                        return func(self)
                    except RuntimeError:
                        dialog = Gtk.MessageDialog(
                            self, 0, Gtk.MessageType.WARNING,
                            Gtk.ButtonsType.OK, message)
                        dialog.run()
                        dialog.destroy()
            return wrapper
        return decorator

    @_warning("Invalid coordinates format")
    def run(self):
        result = super(EntryDialog, self).run()
        if result == Gtk.ResponseType.OK:
            text = self._coordinates_entry.get_text()
            if not EntryDialog.COORDINATES_PATTERN.match(text):
                raise RuntimeError("error")
            return True
        return False

    @property
    def name(self):
        return self._name_entry.get_text()

    @property
    def coordinates(self):
        return self._coordinates_entry.get_text()

    @property
    def wrap(self):
        return self._check.get_active()
