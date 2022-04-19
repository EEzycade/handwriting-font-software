from functools import wraps
from flask import request, jsonify, abort
from app import app

def check_key(key, ip):
    """
    Summary: Check API Key and IP.
    Author: Hans Husurianto

    @param key: API Key to check.
    @param ip: IP of the requester.
    @return: boolean
    """
    if key is None or ip is None:
        return False
    api_key = app.config['API_KEY']
    if api_key is None:
        return False
    elif api_key == key and ip == app.config['IP']:
        return True
    return False

def requires_auth(f):
    """
    Summary: Decorator to check API Key and IP.
    @param f: flask function
    @return: decorator, return the wrapped function
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if app.config["DEBUG"] or check_key(request.headers['key'], request.remote_addr):
            return f(*args, **kwargs)
        else:
            abort(401, "Unauthorized API key. Please check your API key and that you have spelt it correctly.")
    return decorated

def devEnvironment(f):
    """
    Summary: Decorator to check if the app is in development environment.
    @param f: flask function
    @return: decorator, return the wrapped function
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if app.config["DEBUG"]:
            return f(*args, **kwargs)
        else:
            abort(403, "Forbidden. This endpoint is not available in production environment.")
    return decorated