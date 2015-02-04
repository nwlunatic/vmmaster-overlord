# coding: utf-8
from threading import Thread
from time import sleep


class StoppableThread(Thread):
    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self.daemon = True
        self.running = True

    def stop(self):
        self.running = False


class TargetRepeatingThread(StoppableThread):
    def __init__(self, target=None, yield_time=0.1, *args, **kwargs):
        target = self.__repeatable(target)
        super(TargetRepeatingThread, self).__init__(target=target, *args, **kwargs)
        self.yield_time = yield_time

    def __repeatable(self, target):
        def wrapper(*args, **kwargs):
            while self.running:
                target(*args, **kwargs)
                sleep(self.yield_time)
        return wrapper