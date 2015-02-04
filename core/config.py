# coding: utf-8
import os
import imp
import traceback

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

from .log import get_logger
import logging
log = get_logger(__name__, logging.INFO)


def split_path(path):
    sep_index = path.rfind(os.path.sep)
    if sep_index > 0:
        filename = path[sep_index:]
        location = path[:sep_index]
    else:
        filename = path
        location = "."

    return filename, location


class ConfigReader(object):
    def __init__(self, path):
        self.path = path
        self.config = {}

    def read(self):
        try:
            loaded_config = imp.load_source('__loading_config__', self.path)
        except:
            log.error(traceback.format_exc())
            loaded_config = None
        for name in dir(loaded_config):
            if not (name.startswith("__") or name.endswith("__")):
                self.config[name] = getattr(loaded_config, name)


class ConfigChangeHandler(FileSystemEventHandler):
    def __init__(self, name, reader):
        super(ConfigChangeHandler, self).__init__()
        self.name = name
        self.reader = reader

    def on_modified(self, event):
        if type(event) is not FileModifiedEvent:
            return

        if event.src_path.endswith(self.name):
            log.info("Config modified")
            self.reader.read()


class ConfigLoader(object):
    def __init__(self, path):
        self._reader = ConfigReader(path)
        self._reader.read()
        name, location = split_path(path)
        self._event_handler = ConfigChangeHandler(name, self._reader)
        self._observer = Observer()
        self._observer.schedule(self._event_handler, location, recursive=False)
        self._observer.start()

    def __del__(self):
        self.stop()

    def stop(self):
        self._observer.stop()
        self._observer.join()

    @property
    def config(self):
        return self._reader.config


config_loader = ConfigLoader("./settings.py")
config = config_loader.config