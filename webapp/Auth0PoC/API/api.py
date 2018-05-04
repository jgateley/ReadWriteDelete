"""
Flask API implementation of a very simple RESTful api.
It supports a database of items, allowing reading, writing and deleting
GET /items - lists all items
POST /items - adds a new item
GET /items/<key> - Gets an item by key
DELETE /items/<key> - Deletes an item by key

The database is actually handled by Django's ORM, even though the Django app does not directly access the database.
Instead the Django app calls this API.

All API calls require authentication
"""

from flask import Flask, jsonify, request, _request_ctx_stack
from functools import wraps
from jose import jwt
import json
from six.moves.urllib.request import urlopen

import django
django.setup()

from ReadWriteDelete import models

app = Flask(__name__)


AUTH0_DOMAIN = 'johngateley.auth0.com'
API_IDENTIFIER = 'http://auth0.johngateley.com:5010/'
ALGORITHMS = ["RS256"]


# Format error response and append status code.
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


def get_token_auth_header():
    """Obtains the access token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                        "description":
                            "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must start with"
                            " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                        "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must be"
                            " Bearer token"}, 401)

    token = parts[1]
    return token


def requires_scope(required_scope):
    """Determines if the required scope is present in the access token
    Args:
        required_scope (str): The scope required to access the resource
    """
    token = get_token_auth_header()
    unverified_claims = jwt.get_unverified_claims(token)
    if unverified_claims.get("scope"):
        token_scopes = unverified_claims["scope"].split()
        for token_scope in token_scopes:
            if token_scope == required_scope:
                return True
    return False


def requires_auth(f):
    """Determines if the access token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        try:
            unverified_header = jwt.get_unverified_header(token)
        except jwt.JWTError:
            raise AuthError({"code": "invalid_header",
                            "description":
                                "Invalid header. "
                                "Use an RS256 signed JWT Access Token"}, 401)
        if unverified_header["alg"] == "HS256":
            raise AuthError({"code": "invalid_header",
                            "description":
                                "Invalid header. "
                                "Use an RS256 signed JWT Access Token"}, 401)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=API_IDENTIFIER,
                    issuer="https://"+AUTH0_DOMAIN+"/"
                )
            except jwt.ExpiredSignatureError:
                raise AuthError({"code": "token_expired",
                                "description": "token is expired"}, 401)
            except jwt.JWTClaimsError:
                raise AuthError({"code": "invalid_claims",
                                "description":
                                    "incorrect claims,"
                                    " please check the audience and issuer"}, 401)
            except Exception:
                raise AuthError({"code": "invalid_header",
                                "description":
                                    "Unable to parse authentication"
                                    " token."}, 401)

            _request_ctx_stack.top.current_user = payload
            return f(*args, **kwargs)
        raise AuthError({"code": "invalid_header",
                        "description": "Unable to find appropriate key"}, 401)
    return decorated


@app.route('/items')
@requires_auth
def get_items():
    """
    Gets all items
    :return: the list of items
    """
    return jsonify(models.Item.list())


@app.route('/items', methods=['POST'])
@requires_auth
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


@app.route('/items/<key>')
@requires_auth
def show_item(key):
    """
    Get a single item.
    :param key:
    :return: either json version of the item or an error string X 404
    """
    result = models.Item.get(key)
    if result is None:
        return 'Item ' + str(key) + ' not found', 404
    else:
        return jsonify(result)


@app.route('/items/<key>', methods=['DELETE'])
@requires_auth
def delete_item(key):
    """
    Delete an item.
    :param key: The item to delete
    :return: string or empty, HTTP code
    """
    if not models.Item.remove(key):
        return 'Item ' + str(key) + ' not found', 404
    return '', 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010)
