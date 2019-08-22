import re
from gi.repository import Gtk


class EntryDialog(Gtk.MessageDialog):

    COORDINATES_PATTERN = re.compile(r"(-?\d+,-?\d+;)*-?\d+,-?\d+")

    def __init__(self, text, hint):
        super(EntryDialog, self).__init__()

        # build the label widget with the message
        self.vbox.pack_start(Gtk.Label(text), False, False, 0)

        # build entry widget
        self._entry = Gtk.Entry()
        self._entry.set_text(hint)
        self._entry.connect(
            "activate", lambda ent, dlg, resp: dlg.response(resp), self,
            Gtk.ResponseType.OK)
        self.vbox.pack_start(self._entry, False, False, 0)

        # build the wrap object check box
        self._check = Gtk.CheckButton("Connect last point to the first one")
        self._check.set_active(True)
        self.vbox.pack_start(self._check, False, False, 0)

        self.set_size_request(400, 0)
        self.show_all()

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
            text = self._entry.get_text()
            if not EntryDialog.COORDINATES_PATTERN.match(text):
                raise RuntimeError("error")
            return text, self._check.get_active()
        return None, None
