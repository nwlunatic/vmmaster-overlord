#!/usr/bin/env bash
venv/bin/twistd -n web --wsgi app.app --port 5000
