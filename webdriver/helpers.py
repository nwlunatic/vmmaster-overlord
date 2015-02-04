# coding: utf-8
import json

from flask import current_app, request, stream_with_context, Response
from twisted.web.wsgi import _InputStream
from requests import request as make_request


class NoSuchPlatform(Exception):
    pass


def get_desired_capabilities(data):
    return json.loads(data).get("desiredCapabilities")


def check_platform(platform):
    platforms = []
    for node in current_app.nodes:
        platforms += node.platforms

    if not platform in platforms:
        raise NoSuchPlatform(platform)


def request_closed():
    if isinstance(request.input_stream, _InputStream):
        return request.input_stream._wrapped.closed
    else:
        return request.input_stream.closed


def proxy(node):
    response = make_request(
        request.method,
        "http://%s:%s/%s" % (node.host, node.port, request.path),
        data=request.data,  stream=True)
    return Response(stream_with_context(response.iter_content()), content_type=response.headers['content-type'])


def parse_session_id(response):
    return json.loads(response.data).get("sessionId")


def get_new_session(dc):
    session = current_app.queue.enqueue(dc)
    from time import sleep
    while not request_closed() and session.node is None:
        sleep(0.1)

    response = proxy(session.node)
    session.node.unlock()
    current_app.sessions.add(parse_session_id(response), session.node)
    return response


def delete_session(session_id):
    node = current_app.sessions.node(session_id)
    response = proxy(node)
    current_app.sessions.remove(session_id)
    return response