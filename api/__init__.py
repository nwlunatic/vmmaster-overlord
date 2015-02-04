# coding: utf-8
from __future__ import print_function

from flask import Blueprint, jsonify, current_app
api = Blueprint('api', __name__)


@api.route('/nodes')
def nodes():
    context = {
        'nodes': current_app.nodes
    }
    return jsonify(context)


@api.route('/platforms')
def platforms():
    context = {
        "platforms": current_app.nodes.platforms
    }
    return jsonify(context)


@api.route('/queue')
def queue():
    context = {
        "queue": current_app.queue
    }
    return jsonify(context)


@api.route('/sessions')
def sessions():
    context = {
        "sessions": current_app.sessions
    }
    return jsonify(context)


@api.route('/status')
def status():
    context = {
        "sessions": current_app.sessions,
        "queue": current_app.queue,
        "nodes": current_app.nodes,
        "platforms": current_app.nodes.platforms,
    }
    return jsonify(context)