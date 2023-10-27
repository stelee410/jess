import requests
import os
import ernie
from functools import wraps

GET_TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"


def _check_api_keys():
    if ernie.api_key is None:
        raise Exception('API_KEY is not set')
    if ernie.secret_key is None:
        raise Exception('SECRET_KEY is not set')

def check_api_keys(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        _check_api_keys()
        return f(*args, **kwargs)
    return decorated_function

@check_api_keys
def get_access_token():
    params = {"grant_type": "client_credentials", "client_id": ernie.api_key, "client_secret": ernie.secret_key}
    return str(requests.post(GET_TOKEN_URL, params=params).json().get("access_token"))