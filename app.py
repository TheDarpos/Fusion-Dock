import gi
import math
import cairo
import numpy
from dock import Dock, create_icon, get_gicon_pixbuf, pixbuf2image

gi.require_version('Gtk', '3.0')  # noqa
gi.require_version('Gdk', '3.0')  # noqa
gi.require_version('Gio', '2.0')  # noqa
gi.require_version('GObject', '2.0')  # noqa

from applications import AppCache, WindowTracker, groupings
from PIL import Image, ImageOps
from gi.repository import Gtk, Gdk, Gio, GLib, GObject
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

        self.connect("screen-changed", self.screen_changed)
        self.connect("draw", self.expose_draw)

        self.set_decorated(False)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)

        self.set_type_hint(Gdk.WindowTypeHint.DOCK)

        dock = Dock(None, app_cache=app_cache, window_tracker=window_tracker)
        self.add(dock)

        style_provider = Gtk.CssProvider()
        style_provider.load_from_file(Gio.File.new_for_path("style.css"))

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        def aaa(_, a):
            print("aaa")
            #self.resize(
            #    max(dock.get_size_request().width, 1), max(dock.get_size_request().height, 1))
            # self.set_size_request(100, 100)
            # self.resize(100, 100)
            print(dock.get_size_request())
        # dock.connect("draw", lambda dock, _: self.resize(
        #  max(dock.get_size_request().width, 1), max(dock.get_size_request().height, 1)))
        dock.connect("draw", aaa)

        self.screen_changed(self, None, None)

        self.show_all()
        self.resize(100, 100)
        Gtk.main()


    def expose_draw(self, widget, event, userdata=None):
        cr = Gdk.cairo_create(widget.get_window())
        cr.scale(.2, .2)

        if self.supports_alpha:
            print("setting transparent window")
            cr.set_source_rgba(1.0, 1.0, 1.0, 0.0)
        else:
            print("setting opaque window")
            cr.set_source_rgb(1.0, 1.0, 1.0)

        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()

        return False

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
