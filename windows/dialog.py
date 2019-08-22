import re
from gi.repository import Gtk


class EntryDialog(Gtk.MessageDialog):

    COORDINATES_PATTERN = re.compile(r"(-?\d+,-?\d+;)*-?\d+,-?\d+")

    def __init__(self, text, hint):
        super(EntryDialog, self).__init__()

        # build the label widget with a message
        label = Gtk.Label()
        label.set_text(text)
        self.vbox.pack_start(label, True, True, 0)

        # build entry widget
        self._entry = Gtk.Entry()
        self._entry.set_text(hint)
        self._entry.connect(
            "activate", lambda ent, dlg, resp: dlg.response(resp), self,
            Gtk.ResponseType.OK)
        self.vbox.pack_start(self._entry, False, False, 0)

        self.set_size_request(400, 0)
        self.show_all()

    def run(self):
        while True:
            try:
                return self._run()
            except RuntimeError:
                warning = Gtk.MessageDialog(
                    self, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK,
                    "Invalid format for coordinates")
                warning.run()
                warning.destroy()

    def _run(self):
        result = super(EntryDialog, self).run()
        if result == Gtk.ResponseType.OK:
            text = self._entry.get_text()
            if not EntryDialog.COORDINATES_PATTERN.match(text):
                raise RuntimeError("error")
            return text
        return None
