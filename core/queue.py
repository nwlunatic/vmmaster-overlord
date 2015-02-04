# coding: utf-8
from copy import copy

from .utils import TargetRepeatingThread
from .node import nodes
from .log import get_logger
log = get_logger(__name__)


class SessionQueue(list):
    def enqueue(self, dc):
        delayed_session = DelayedSession(dc)
        self.append(delayed_session)
        return delayed_session


class DelayedSession(object):
    def __init__(self, dc):
        self.dc = dc
        self.node = None

    def to_json(self):
        return self.dc


class SessionQueueWorker(object):
    def __init__(self, queue=None):
        if queue is None:
            queue = SessionQueue()

        self.queue = queue
        self.worker = TargetRepeatingThread(target=self.work)
        self.worker.start()

    def stop(self):
        self.worker.stop()
        self.worker.join()
        log.info("Session Queue Worker stopped")

    def work(self):
        for session in copy(self.queue):
            node = nodes.get_node_by_dc(session.dc)
            if node:
                session.node = node
                self.queue.remove(session)