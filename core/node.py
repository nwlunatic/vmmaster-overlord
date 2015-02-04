# coding: utf-8
import json
from time import time

import requests

from .config import config
from .log import get_logger
log = get_logger("CONFIG")
from .utils import TargetRepeatingThread


class Node(object):
    status = "unknown"
    name = None
    host = None
    port = None
    platforms = None
    queue = None
    sessions = None
    pool = None
    can_produce = 0
    latency = None
    locked = False

    def __init__(self, name, host, port):
        self.name = name
        self.host = host
        self.port = port
        self.renew_info()
        self.status_poller = TargetRepeatingThread(
            target=self.reload_info, yield_time=config.get("NODE_POLLING_FREQUENCY"), name="Node_Status_Thread-%s" % self.name)
        self.status_poller.start()
        log.info("Node started: %s %s %s" % (self.name, self.host, self.port))

    def stop(self):
        self.status_poller.stop()
        self.status_poller.join()
        log.info("Node stopped: %s %s %s" % (self.name, self.host, self.port))

    def renew_info(self, response=None):
        if not response:
            content = {}
        else:
            content = json.loads(response.content)

        result = content.get("result", {})
        pool = result.get("pool", {})
        self.pool = pool.get("pool", {})
        self.can_produce = pool.get("can_produce", 0)
        self.sessions = result.get("sessions", [])
        self.platforms = result.get("platforms", [])
        self.queue = result.get("queue", [])

    def reload_info(self):
        _start = time()
        try:
            response = requests.get("http://%s:%s/api/status" % (self.host, self.port))
        except requests.ConnectionError:
            self.status = "offline"
            response = None
        self.latency = time() - _start
        self.renew_info(response)
        if response is not None:
            if response.status_code != 200:
                self.status = "bad"
            elif response:
                self.status = "online"

    @property
    def info(self):
        return {
            "status": self.status,
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "platforms": self.platforms,
            "sessions": self.sessions,
            "queue": self.queue,
            "pool": self.pool,
            "can_produce": self.can_produce,
            "latency": self.latency
        }

    def to_json(self):
        return self.info

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False


class Nodes(object):
    def __init__(self):
        log.info("starting nodes")
        self.nodes = []
        nodes = config.get("NODES", {})
        self._add_nodes(nodes)
        self.reloader = TargetRepeatingThread(
            target=self.reload, yield_time=config.get("NODES_RELOAD_FREQUENCY"), name="Nodes_Reloader_Thread")
        self.reloader.start()
        log.info("Nodes started")

    def stop(self):
        for node in self.nodes:
            node.stop()
        self.reloader.stop()
        self.reloader.join()
        log.info("Nodes preloader stopped")

    def __iter__(self):
        return iter(self.nodes)

    def _add_nodes(self, nodes):
        self.nodes.extend([Node(**node) for node in nodes])

    def _remove_nodes_by_names(self, names):
        removable_nodes = [node for node in self.nodes if node.name in names]
        for r_node in removable_nodes:
            self.nodes.remove(r_node)

    def reload(self):
        nodes = config.get("NODES", {})
        have = set([node.name for node in self.nodes])
        need = set([node.get("name") for node in nodes])
        to_add = need - have
        to_delete = have - need
        self._add_nodes([node for node in nodes if node.get("name") in to_add])
        self._remove_nodes_by_names(to_delete)

    def get_node_by_dc(self, dc):
        platform = dc.get("platform")
        for node in self.nodes:
            if node.locked:
                continue

            node.lock()
            if platform in node.pool.keys():
                node.pool[platform] -= 1
                return node

            if platform in node.platforms and node.can_produce > 0:
                node.can_produce -= 1
                return node
            node.unlock()

    @property
    def platforms(self):
        platforms = []
        for node in self.nodes:
            platforms += node.platforms
        return platforms

    def to_json(self):
        return self.nodes


nodes = Nodes()