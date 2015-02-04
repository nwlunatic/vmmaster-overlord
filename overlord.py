from __future__ import print_function

import atexit
from flask import Flask
from flask.json import JSONEncoder as FlaskJSONEncoder


from core.node import nodes
from core.queue import SessionQueueWorker
from core.config import config
from core.log import get_logger
from core.session import sessions


log = get_logger(__name__)


class JSONEncoder(FlaskJSONEncoder):
    def default(self, obj):
        if hasattr(obj, "to_json"):
            return obj.to_json()
        return super(JSONEncoder, self).default(obj)


def register_blueprints(app):
    from api import api
    from webdriver import webdriver
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(webdriver, url_prefix='/wd/hub')


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    app.json_encoder = JSONEncoder
    register_blueprints(app)
    queue_worker = SessionQueueWorker()

    app.nodes = nodes
    app.queue = queue_worker.queue
    app.sessions = sessions

    atexit.register(app.nodes.stop)
    atexit.register(queue_worker.stop)
    return app


if __name__ == '__main__':
    create_app().run(debug=True)