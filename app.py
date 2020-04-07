import gi
import math
import cairo
import numpy
from dock import Dock

gi.require_version('Gtk', '3.0')  # noqa
gi.require_version('Gdk', '3.0')  # noqa
gi.require_version('Gio', '2.0')  # noqa

from applications import AppCache, WindowTracker, groupings
from PIL import Image, ImageOps
from gi.repository import Gtk, Gdk, Gio
from dominantcolors import rgba2rgb, find_dominant_colors

app_cache = AppCache()
window_tracker = WindowTracker()


class DockWindow(Gtk.Window):
    supports_alpha = False

    def __init__(self):
        super().__init__()

        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_title("Diffusion Dock")
        self.connect("delete-event", Gtk.main_quit)

        self.set_app_paintable(True)

        # self.connect("screen-changed", self.screen_changed)

        self.set_decorated(False)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)

        self.add(Dock(None, app_cache=app_cache, window_tracker=window_tracker))

        style_provider = Gtk.CssProvider()
        style_provider.load_from_file(Gio.File.new_for_path("style.css"))

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # self.connect("draw", lambda widget, _: widget.resize(
        #    max(self.icon_box.get_size_request().width, 1), max(self.icon_box.get_size_request().height, 1)))

        self.screen_changed(self, None, None)

        self.show_all()
        Gtk.main()

    def screen_changed(self, widget, old_screen, userdata=None):
        screen = self.get_screen()
        visual = screen.get_rgba_visual()

        if visual is None:
            visual = screen.get_system_visual()
            self.supports_alpha = False
        else:
            self.supports_alpha = True

        self.set_visual(visual)


if __name__ == "__main__":
    DockWindow()
