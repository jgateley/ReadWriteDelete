"""
Flask API implementation of a very simple RESTful api.
It supports a database of items, allowing reading, writing and deleting
GET /items - lists all items
POST /items - adds a new item
GET /items/<key> - Gets an item by key
DELETE /items/<key> - Deletes an item by key

The database is actually handled by Django's ORM, even though the Django app does not directly access the database.
Instead the Django app calls this API.
"""

from flask import Flask, jsonify, request

import django
django.setup()

from ReadWriteDelete import models

app = Flask(__name__)


@app.route('/items')
def get_items():
    """
    Gets all items
    :return: the list of items
    """
    return jsonify(models.Item.list())


@app.route('/items', methods=['POST'])
def add_item():
    """
    Add a new item. Return string is empty or an error message
    :return: string, error code
    """
    new_item = request.get_json()
    if 'key' not in new_item or 'value' not in new_item:
        return 'Item requires both key and value', 400
    if new_item['key'] == '':
        return 'Item must have non-empty key', 400
    if not models.Item.make(new_item['key'], new_item['value']):
        return 'Item: ' + new_item['key'] + ' already exists', 400
    return '', 204


@app.route('/items/<int:key>')
def show_item(key):
    """
    Get a single item.
    :param key:
    :return: either json version of the itehm or an error string X 404
    """
    result = models.Item.get(key)
    if result is None:
        return 'Item ' + str(key) + ' not found', 404
    else:
        return jsonify(result)


@app.route('/items/<int:key>', methods=['DELETE'])
def delete_item(key):
    """
    Delete an item.
    :param key: The item to delete
    :return: string or empty, HTTP code
    """
    if not models.Item.remove(key):
        return 'Item ' + str(key) + ' not found', 404
    return '', 204
