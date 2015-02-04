# coding: utf-8
from __future__ import print_function

from flask import Blueprint, jsonify, current_app, request

import helpers

webdriver = Blueprint('webdriver', __name__)


@webdriver.errorhandler(Exception)
def handle_errors(error):
    error_context = {
        'status': 1,
        'value': "%s: %s" % (error.__class__.__name__, error.message)
    }
    return jsonify(error_context)


@webdriver.route('/session', methods=['POST'])
def session():
    dc = helpers.get_desired_capabilities(request.data)
    helpers.check_platform(dc.get("platform"))
    return helpers.get_new_session(dc)


@webdriver.route('/session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    return helpers.delete_session(session_id)


@webdriver.route("/session/<session_id>/<path:url>", methods=['GET', 'POST', 'DELETE'])
def proxy(session_id, url):
    node = current_app.sessions.node(session_id)
    return helpers.proxy(node)
