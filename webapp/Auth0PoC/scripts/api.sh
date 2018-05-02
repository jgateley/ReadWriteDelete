#!/bin/sh

# Script to run the flask process
export FLASK_APP=../API/api.py
export DJANGO_SETTINGS_MODULE=Auth0PoC.settings
flask run -h 0.0.0.0 --port=5010
