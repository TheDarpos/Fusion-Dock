import gi
import os
import pathlib

gi.require_version('Gio', '2.0')

from gi.repository import Gio
from xdg import XDG_DATA_DIRS


#from .applications import xdg_dirs

# DEBUG
xdg_dirs = XDG_DATA_DIRS + \
    [pathlib.Path(os.path.join(os.path.expanduser("~"), ".local", "share"))]

vendor_prefixes = ["gnome-",
                   "fedora-",
                   "mozilla-",
                   "debian-"]


class AppCache(object):
    def __init__(self, load_applications=True):
        if load_applications:
            self.load_applications()

    def load_applications(self):
        self.applications = {}

        for directory in xdg_dirs:
            has_been_set = []

            applications_folder = os.path.join(
                directory.resolve(), "applications")

            try:
                entries = os.scandir(applications_folder)

                for entry in entries:
                    if entry.is_dir(follow_symlinks=True):
                        for root, _, files in os.walk(entry):
                            for file in files:
                                if file.endswith(".desktop"):
                                    full_path = os.path.join(root, file)
                                    desktop_id = "-".join(os.path.relpath(
                                        full_path, start=applications_folder).split(os.sep))

                                    try:
                                        self.applications[desktop_id] = Gio.DesktopAppInfo.new_from_filename(
                                            full_path)
                                        has_been_set.append(desktop_id)
                                    except:
                                        pass
                    elif entry.is_file(follow_symlinks=True):
                        if entry.name.endswith(".desktop"):
                            if not entry.name in has_been_set:
                                try:
                                    self.applications[entry.name] = Gio.DesktopAppInfo.new_from_filename(
                                        entry.path)
                                except:
                                    pass
            except:
                pass

    def lookup_with_prefix(self, basename):
        if not basename.endswith(".desktop"):
            basename += ".desktop"

        if basename in self.applications:
            return self.applications[basename]

        for prefix in vendor_prefixes:
            full_name = prefix + basename

            if full_name in self.applications:
                return self.applications[full_name]

    def get_appinfo_for_wmclass(self, wmclass):
        # First lookup StartupWMClass
        possible = None

        if not self.applications:
            self.load_applications()

        for desktop_id in self.applications:
            if self.applications[desktop_id].get_startup_wm_class() == wmclass:
                if desktop_id == wmclass:
                    return self.applications[desktop_id]
                elif not possible:
                    possible = self.applications[desktop_id]

        if possible:
            return possible

        # Using wmclass as basename, keep case then lowercase
        lookup = self.lookup_with_prefix(wmclass)

        if lookup:
            return lookup
        else:
            lookup = self.lookup_with_prefix(wmclass.lower())
            return lookup

