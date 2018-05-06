import argparse
import requests


def get_oauth_token():
    """
    Get an access token.
    Client values are hard-coded.
    :return:
    """
    r = requests.post('https://johngateley.auth0.com/oauth/token',
                      headers={'content-type': 'application/json'},
                      json={'client_id': '2mRMLBixsqq2wKynxArHOADgL1Eoc3Yb',
                            'client_secret': 'acU5nbJgElE_MPLR8GvJhT3ridoDqyOnrgNiN6zZ0mP0WiPRJNQmBmbWuKxPw8hp',
                            'audience': 'http://auth0.johngateley.com:5010/',
                            'grant_type': 'client_credentials'})
    result = r.json()
    return result


def build_headers(token_dict, is_post=False):
    """
    Build the headers for an API call.
    Headers include the authorization header (with the access token, if present in the token dictionary)
    and the content type json header (if it is a post
    :param token_dict:
    :param is_post:
    :return:
    """
    headers = {}
    if 'token_type' in token_dict:
        headers['authorization'] = token_dict['token_type'] + ' ' + token_dict['access_token']
    if is_post:
        headers['content-type'] = 'application/json'
    return headers


def api_get(token_dict, url):
    """
    Do a get on the API and raise an exception if it fails
    :param token_dict:
    :param url:
    :return:
    """
    r = requests.get(url,
                     headers=build_headers(token_dict))
    if r.status_code != 200:
        raise Exception("Couldn't do get")
    return r.json()


def api_post(token_dict, url, json):
    """
    Do a post on the API and raise an exception if it fails
    :param token_dict:
    :param url:
    :param json:
    :return:
    """
    r = requests.post(url,
                      headers=build_headers(token_dict, True),
                      json=json)
    if r.status_code >= 300:
        raise Exception("Couldn't do post")


def api_delete(token_dict, url):
    """
    Do a delete on the API and raise an exception if it fails
    :param token_dict:
    :param url:
    :return:
    """
    r = requests.delete(url,
                        headers=build_headers(token_dict))
    if r.status_code >= 300:
        raise Exception("Couldn't do delete")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Get a token and test an API")
    args = parser.parse_args()

    endpoint = 'http://127.0.0.1:5010/items'
    test_key = 'xxxyyyzzzzzzyyy'

    # Make sure the api fails if not authenticated
    # Only testing one call, though really should test all
    # It is harder to write tests that accurately test things like a single item detail
    # since you have to ensure the item exists, and the failure is in the authentication
    token_info = {}
    exception_raised = False
    try:
        items = api_get(token_info, endpoint)
    except Exception:
        exception_raised = True
    if not exception_raised:
        raise Exception("Get succeeded and it shouldn't have")

    token_info = get_oauth_token()
    items = api_get(token_info, endpoint)
    item = api_get(token_info, endpoint + '/' + items[0]['key'])
    api_post(token_info, endpoint, {"key": test_key, "value": "plugh"})
    api_delete(token_info, endpoint + '/' + test_key)

    # Test with invalid access token.
    # Again, only test one case, though all should really be tested
    access_token = token_info['access_token']
    char = access_token[0]
    if char == 'A':
        char = 'B'
    else:
        char = 'A'
    token_info['access_token'] = char + access_token[1:]
    exception_raised = False
    try:
        items = api_get(token_info, endpoint)
    except Exception:
        exception_raised = True
    if not exception_raised:
        raise Exception("Get succeeded and it shouldn't have")
