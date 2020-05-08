import gi
import os
import pathlib

gi.require_version('Gio', '2.0')  # noqa
gi.require_version('Gtk', '3.0')  # noqa

from xdg import XDG_DATA_DIRS
from gi.repository import Gio, Gtk


xdg_dirs = XDG_DATA_DIRS + [pathlib.Path(os.path.join(os.path.expanduser("~"), ".local", "share"))]

def get_icon_pixbuf_for_appinfo(appinfo):
    icon = appinfo.get_icon()
    return get_gicon_pixbuf(icon)

def get_gicon_pixbuf(icon):
    if icon:
        icon_info = Gtk.IconTheme.get_default().lookup_by_gicon_for_scale(icon, 512, 1, Gtk.IconLookupFlags.USE_BUILTIN)

        if icon_info:
            return icon_info.load_icon()
