"""Python Flask WebApp Auth0 integration example
"""
from authlib.client import OAuthException
from authlib.flask.client import OAuth
from werkzeug.exceptions import HTTPException
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from functools import wraps
import requests
from six.moves.urllib.parse import urlencode

""" Constants
"""
PROFILE_KEY = 'profile'
SECRET_KEY = 'Neveruseadefaultsecretkeyyoushouldalwaysmakeoneup123andmaybe12345stickinsometyops'
JWT_PAYLOAD = 'jwt_payload'
ACCESS_TOKEN = 'access_token'

AUTH0_CLIENT_ID = '4wZYFmihsJ96V6Mf0uHUBxuQ23EfJceU'
AUTH0_DOMAIN = 'johngateley.auth0.com'
AUTH0_CLIENT_SECRET = 'DdJk7skN4nKcCfXIBYRNm67HYKJXUzi6ns9LTDxh5wMdMbZV9wqGu-BnnNku0zJV'
AUTH0_CALLBACK_URL = 'http://localhost:4005/callback'
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = AUTH0_BASE_URL + '/userinfo'
CUSTOM_AUDIENCE = 'http://auth0.johngateley.com:5010/'

app = Flask(__name__, static_url_path='/public', static_folder='./public')
app.secret_key = SECRET_KEY
app.debug = True


@app.errorhandler(Exception)
def handle_auth_error(ex):
    """
    Handle Auth0 exceptions
    :param ex:
    :return:
    """
    response = jsonify(message=str(ex))
    response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
    return response


oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={
        'scope': 'openid profile',
    },
)


def requires_auth(f):
    """
    Decorator that checks for the profile in the session.
    If it is not there, we are not logged in
    :param f:
    :return:
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if PROFILE_KEY not in session:
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated


# Controllers API
@app.route('/')
def home():
    """
    Login page
    :return:
    """
    return render_template('index.html')


@app.route('/callback')
def callback_handling():
    """
    After Auth0 authenticates a user, save the needed info in the session, then redirect to the items page
    :return:
    """
    try:
        resp = auth0.authorize_access_token()
    except OAuthException:
        return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=CUSTOM_AUDIENCE)

    url = AUTH0_BASE_URL + '/userinfo'
    headers = {'authorization': 'Bearer ' + resp['access_token']}
    resp = requests.get(url, headers=headers)
    userinfo = resp.json()

    session[ACCESS_TOKEN] = headers

    session[JWT_PAYLOAD] = userinfo

    session[PROFILE_KEY] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }

    return redirect('/items')


@app.route('/login')
def login():
    """
    'Invisible' page that redirects to the auth0 authentication page, with the callback url and audience set
    :return:
    """
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=CUSTOM_AUDIENCE)


@app.route('/logout')
def logout():
    """
    Clear the session and redirect to the Auth0 logout page
    :return:
    """
    session.clear()
    params = {'returnTo': url_for('home', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


# This was ported from Django. Django has built in CSRF prevention
# I'm not sure how to do this in Flask, but it must be fixed.
@app.route('/items', methods=('GET', 'POST'))
@requires_auth
def items():
    """
    List items, and add a new item (if POST)
    :return:
    """
    access_token = session[ACCESS_TOKEN]
    error_message = ''
    if request.method == 'POST':
        r = requests.post('http://localhost:5010/items',
                          headers=access_token,
                          json={'key': request.form['key'], 'value': request.form['value']})
        if r.status_code == 401:
            error_message = 'Unauthorized to create'
        elif r.status_code != 204:
            error_message = r.content
    r = requests.get('http://localhost:5010/items', headers=access_token)
    if r.status_code == 401:
        error_message = 'Unauthorized to list'
    items_info = r.json()
    return render_template('items.html',
                           error_message=error_message,
                           items=items_info,
                           userinfo=session[PROFILE_KEY])


@app.route('/item/<string:key>', methods=('GET', 'POST'))
@requires_auth
def item(key):
    """
    Details on a single item, or delete it (if POST)
    :param key:
    :return:
    """
    access_token = session[ACCESS_TOKEN]
    error_message = ''
    item_info = None
    if request.method == 'POST':
        r = requests.delete('http://localhost:5010/items/' + key, headers=access_token)
        if r.status_code == 401:
            error_message = 'Unauthorized to delete'
        elif r.status_code != 204:
            error_message = r.content
        else:
            return redirect('/items')
    r = requests.get('http://localhost:5010/items/' + key, headers=access_token)
    if r.status_code == 401:
        error_message = 'Unauthorized to list'
    elif r.status_code != 200:
        error_message = 'Item not found'
    else:
        item_info = r.json()
    return render_template('item.html', error_message=error_message, item=item_info)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4005)
