bl_info = {
    "name": "Auto-Reload Linked Libraries",
    "author": "gandalf3",
    "version": (1, 0, 1),
    "blender": (2, 80, 0),
    "description": "Automatically reload linked libraries when they are modified.",
    "doc_url": "https://github.com/gandalf3/auto-reload-linked-libraries",
    "tracker_url": "https://github.com/gandalf3/auto-reload-linked-libraries/issues",
    "category": "System",
}

import logging
logging.basicConfig(level=logging.WARNING)

logger = logging.getLogger('auto_reload_libraries')
logger.level = logging.INFO

import time
import os
import sys

# XXX add our "statically included" libraries to system include path
sys.path.insert(1, os.path.join(os.path.dirname(__file__), "extern"))

from watchdog.events import FileSystemEventHandler, EVENT_TYPE_OPENED
from watchdog.observers import Observer

import bpy
from bpy.app.handlers import persistent

OBSERVERS = []
SHOULD_RELOAD = False

@persistent
def load_handler(context: bpy.context):
    logger.debug("load_handler running")
    setup_observers()

@persistent
def depsgraph_update_post_handler(scene: bpy.types.Scene, context: bpy.context):
    if len(bpy.data.libraries) != len(OBSERVERS):
        logger.debug("Change in linked libraries detected")
        setup_observers()

def setup_observers():
    logger.debug("clearing OBSERVERS: %s", OBSERVERS)
    for O in OBSERVERS:
        O.stop()
    OBSERVERS.clear()
    logger.debug("cleared OBSERVERS: %s", OBSERVERS)

    for lib in bpy.data.libraries:
        logger.debug("installing observer for %s", lib.name)
        observer = LibraryObserver(lib)
        logger.debug(observer)
        observer.start()
        OBSERVERS.append(observer)

    # Only run timer if there are actually linked libraries
    if (len(OBSERVERS) > 0):
        if (not bpy.app.timers.is_registered(check_if_need_to_reload)):
            bpy.app.timers.register(check_if_need_to_reload, persistent=True)
    else:
        if (bpy.app.timers.is_registered(check_if_need_to_reload)):
            bpy.app.timers.unregister(check_if_need_to_reload)

class AllEventTrigger(FileSystemEventHandler):
    timeout = .3
    last_occurance = 0

    def __init__(self, func):
        self.func = func

    def on_any_event(self, event):
        logger.debug(event)

        if event.event_type == EVENT_TYPE_OPENED:
            logger.debug("ignoring open event")
            return

        now = time.time()
        if (now - self.last_occurance <= self.timeout):
            return

        time.sleep(self.timeout)
        self.func()
        self.last_occurance = time.time()

class DirectoryObserver(Observer):

    watched_directories = {}

    def __init__(self, directory, callback):
        super().__init__()

        self.directory = directory
        self.callback = callback

        if directory not in self.watched_directories:
            self.watched_directories[self.directory] = [callback]
            self.schedule(
                AllEventTrigger(self.call_callbacks), self.directory, recursive=False
            )

            logger.debug("Watching directory %s", directory)

        else:
            self.watched_directories[self.directory].append(callback)
            logger.debug("Already watching %s", self.directory)

    def call_callbacks(self):
        for cb in self.watched_directories[self.directory]:
            cb()

    def stop(self):
        if self.directory not in self.watched_directories:
            return

        self.watched_directories[self.directory].remove(self.callback)

        if len(self.watched_directories[self.directory]) <= 0:
            del self.watched_directories[self.directory]
            logger.debug("Stopping watching of %s", self.directory)
            super().stop()
            super().join(timeout=3)
            if super().is_alive():
                logger.warning("Timeout while stopping watching of '%s'", self.directory)


class LibraryObserver():

    def __init__(self, library):
        self.is_relative = False
        self.triggered = False

        libpath = library.filepath
        if library.filepath.startswith('//'):
            libpath = os.path.join(\
                                     os.path.dirname(bpy.data.filepath),
                                     library.filepath[2:]
                                     )
            logger.debug("dereferencing relative path: %s -> %s", library.filepath, libpath)
            self.is_relative = True

        self.libname = library.name
        self.directory = os.path.dirname(libpath)
        self.filename = os.path.basename(libpath)
        self.mtime = os.path.getmtime(libpath)
        self.libpath = libpath

        self.directory_observer = DirectoryObserver(self.directory, self.trigger)

    def trigger(self):
        new_mtime = os.path.getmtime(self.libpath)

        if new_mtime > self.mtime:
            logger.debug("%s modified! %s > %s", self.filename, self.mtime, new_mtime)
            global SHOULD_RELOAD
            SHOULD_RELOAD = True
            self.triggered = True
            self.mtime = new_mtime

    def reset(self):
        self.triggered = False

    def start(self):
        self.directory_observer.start()

    def stop(self):
        self.directory_observer.stop()

    def __repr__(self):
        return f"LibraryObserver(<{self.libname}>)"


def check_if_need_to_reload():
    try:
        if SHOULD_RELOAD:
            do_lib_reload()
    except KeyboardInterrupt:
        pass

    return .3

def do_lib_reload():
    for O in OBSERVERS:
        if O.triggered:
            libname = O.libname
            libdir = O.directory
            libfile = O.filename
            logger.info("Reloading %s", libname)
            logger.debug("bpy.ops.wm.lib_reload(library=\"%s\", directory=\"%s\", filename=\"%s\")", libname, libdir, libfile)
            logger.debug(bpy.ops.wm.lib_reload(library=libname, directory=libdir, filename=libfile))

            O.reset()

    global SHOULD_RELOAD
    SHOULD_RELOAD = False

def one_time_setup():
    setup_observers()
    bpy.app.timers.unregister(one_time_setup)
    return 10

def one_time_unsetup():
    logger.debug("clearing OBSERVERS: %s", OBSERVERS)
    for O in OBSERVERS:
        O.stop()
    OBSERVERS.clear()
    bpy.app.timers.unregister(one_time_unsetup)


def register():
    bpy.app.handlers.load_post.append(load_handler)
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_update_post_handler)

    bpy.app.timers.register(one_time_setup, persistent=False)

    # timer registered on-demand, see setup_observers()
    # bpy.app.timers.register(check_if_need_to_reload, persistent=True)

    logger.info("Registered Auto-Reload Libraries")

def unregister():
    bpy.app.handlers.load_post.remove(load_handler)
    bpy.app.handlers.depsgraph_update_post.remove(depsgraph_update_post_handler)
    bpy.app.timers.register(one_time_unsetup, persistent=False)

    if bpy.app.timers.is_registered(check_if_need_to_reload):
        bpy.app.timers.unregister(check_if_need_to_reload)

if __name__ == "__main__":
    register()

