def main():
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk

    from windows.main import MainWindow
    main_window = MainWindow()
    main_window.show()

    Gtk.main()

if __name__ == "__main__":
    main()
