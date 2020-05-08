import gi

gi.require_version('Wnck', '3.0')  # noqa
gi.require_version('GObject', '2.0')  # noqa

from gi.repository import Wnck, GObject
from .app_cache import AppCache

default_screen = Wnck.Screen.get_default()


class WindowData(object):
    __slots__ = ['appinfo', 'is_focused', 'title', 'icon']

    def __init__(self, appinfo, is_focused, title, icon):
        self.appinfo = appinfo
        self.is_focused = is_focused
        self.title = title
        self.icon = icon


class WindowTracker(GObject.Object):
    def __init__(self, *, app_cache=None, screen=default_screen, flter=lambda _: True):
        super().__init__()

        self.app_cache = app_cache or AppCache()
        self.windows = {}
        self.active_window = screen.get_active_window()
        self.screen = screen
        self.handlers = {}
        self.flter = flter

        self.emit("update")

        self.add_handlers()

    @GObject.Signal
    def update(self):
        pass

    def get_groups(self, *, groupby=lambda a, b: False):
        groups = []

        for window in self.windows:
            for group in groups:
                if groupby(group[0], window):
                    group.append(window)
                    break
            else:
                groups.append([window])

        return groups

    def track_by(self, flter=lambda _: True):
        for window in self.screen.get_windows():
            if flter(window):
                self.track(window)

        self.flter = flter

        self.emit("update")

    def window_open(self, _, window):
        if self.flter(window):
            self.track(window)

    def window_close(self, _, window):
        if window in self.windows:
            self.untrack(window)

    def add_handlers(self):
        self.screen.connect("active_window_changed",
                            self.active_window_changed)
        self.screen.connect("window_opened", self.window_open)
        self.screen.connect("window_closed", self.window_close)

    def active_window_changed(self, screen, _):
        self.active_window = screen.get_active_window()

        for window in self.windows:
            if self.windows[window].is_focused and self.active_window != self.windows[window]:
                self.windows[window].is_focused = False

        try:
            self.windows[self.active_window].is_focused = True
        except:
            pass

        self.emit("update")

    def track(self, window):
        self.windows[window] = WindowData(self.app_cache.get_appinfo_for_wmclass(window.get_class_group_name(
        )), self.active_window == window, window.get_name() if window.has_name else "Unknown", window.get_icon() if window.get_icon_is_fallback() else "")
        self.handlers[window] = [window.connect(
            "class-changed", self.window_class_changed)]

        self.emit("update")

    def window_class_changed(self, window):
        self.windows[window].appinfo = self.app_cache.get_appinfo_for_wmclass(
            window.get_class_group_name())

        self.emit("update")

    def untrack(self, window):
        for handler in self.handlers[window]:
            window.disconnect(handler)

        del self.windows[window]

        self.emit("update")
