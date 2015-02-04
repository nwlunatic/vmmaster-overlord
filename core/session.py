# coding: utf-8


class Sessions(object):
    map = None

    def __init__(self):
        self.map = dict()

    def add(self, session_id, node):
        self.map[session_id] = node

    def remove(self, session_id):
        del self.map[session_id]

    def node(self, session_id):
        return self.map[session_id]

    def to_json(self):
        return {key:value.name for key, value in self.map.iteritems()}


sessions = Sessions()