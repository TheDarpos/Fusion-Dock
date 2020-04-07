import gi
import math
import cairo
import numpy

gi.require_version('Gtk', '3.0')  # noqa
gi.require_version('Gio', '2.0')  # noqa
gi.require_version('GLib', '2.0')  # noqa
gi.require_version('Wnck', '3.0')  # noqa
gi.require_version('GdkPixbuf', '2.0')  # noqa

from PIL import Image
from gi.repository import Gtk, Gio, GdkPixbuf, GLib, Wnck
from dominantcolors import rgba2rgb, find_dominant_colors
from applications import AppCache, WindowTracker, groupings, get_icon_pixbuf_for_appinfo, get_gicon_pixbuf

default_screen = Wnck.Screen.get_default()


def pixbuf2image(pix):
    data = pix.get_pixels()
    w = pix.props.width
    h = pix.props.height
    stride = pix.props.rowstride
    mode = "RGB"

    if pix.props.has_alpha == True:
        mode = "RGBA"

    im = Image.frombytes(mode, (w, h), data, "raw", mode, stride)
    return im


def image2pixbuf(im):
    arr = numpy.array(im)
    w, h = im.size
    width, height = im.size

    return GdkPixbuf.Pixbuf.new_from_bytes(GLib.Bytes.new(im.tobytes("raw", "RGBA")), GdkPixbuf.Colorspace.RGB,
                                           True, 8, width, height, width * 4)


def create_icon(click_event, *, icon_image, name="Application"):
    arr = numpy.asarray(icon_image)

    if icon_image.mode == 'RGBA':
        arr = rgba2rgb(arr)

    DOT_SPACING = 20
    DOT_SIZE = 5
    MAXIMUM_DOTS = 5
    dot_amount = 0
    dot_color = find_dominant_colors(arr, 1)[0]
    dot_opacity = 1

    icon_pixbuf = image2pixbuf(icon_image)

    icon_pixbuf = icon_pixbuf.scale_simple(
        100, 100, GdkPixbuf.InterpType.BILINEAR)

    def update_dots(amount, color=None, opacity=None):
        nonlocal dot_amount, dot_color, dot_opacity
        dot_amount = min(amount, MAXIMUM_DOTS)
        dot_color = color if color else dot_color
        dot_opacity = opacity if opacity else dot_opacity
        dots.queue_draw()

    def render_dots(widget, ctx):
        cairo_color = [*map(lambda element: element / 255, dot_color)]

        widget_size, _ = widget.get_allocated_size()

        for i in range(dot_amount):
            dot_x = widget_size.width / 2 - ((i - (dot_amount - 1) / 2) *
                                             DOT_SPACING)
            dot_y = widget_size.height / 2

            pat = cairo.RadialGradient(
                dot_x, dot_y, 0.0, dot_x, dot_y, DOT_SIZE)

            pat.add_color_stop_rgb(0, *cairo_color)
            pat.add_color_stop_rgb(0.3, *cairo_color)
            pat.add_color_stop_rgb(
                1, *map(lambda element: min(element + 0.03, 1), cairo_color))

            ctx.arc(dot_x, dot_y, DOT_SIZE, 0, 2 * math.pi)
            ctx.set_source(pat)
            ctx.fill()

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    box.set_tooltip_text(name)

    image = Gtk.Image.new_from_pixbuf(icon_pixbuf)
    dots = Gtk.DrawingArea()
    dots.connect("draw", render_dots)
    dots.set_size_request(-1, DOT_SIZE + 10)
    dots.queue_draw()

    box.add(image)
    box.add(dots)

    return (box, update_dots)


class Dock(Gtk.Box):
    def __init__(self, screen=default_screen, app_cache=None, window_tracker=None):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        self.get_style_context().add_class("dock")
        self.app_cache = app_cache or AppCache(load_applications=True)
        self.window_tracker = window_tracker or WindowTracker(
            app_cache=self.app_cache, screen=screen, flter=self.window_filter)

        self.window_tracker.connect("update", self.rerender)

    def rerender(self, _):
        groups = self.window_tracker.get_groups(
            groupby=groupings.by_wmclass_group)

        for child in self.get_children():
            Gtk.Widget.destroy(child)

        for group in groups:
            app_info = self.app_cache.get_appinfo_for_wmclass(
                group[0].get_class_group_name())

            icon, update_icon = create_icon(lambda: None, icon_image=pixbuf2image(get_icon_pixbuf_for_appinfo(
                app_info) if app_info else get_gicon_pixbuf(Gio.ThemedIcon.new_from_names(["dialog-error-symbolic"]))), name=app_info.get_name() if app_info else group[0].get_name())

            self.add(icon)
            update_icon(len(group))
            print("group added:", app_info.get_name() if app_info else group[0].get_name())
            print(icon.get_size_request())

        self.queue_draw()

    def window_filter(self, window):
        return window.get_window_type() == Wnck.WindowType.NORMAL
