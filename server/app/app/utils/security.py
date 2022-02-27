from functools import wraps
from flask import request, abort
from app import app

# Decorator to require authentication/API Key
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.args.get('key') and request.arges.get('key') == app.config['API_KEY']:
            return f(*args, **kwargs)
        else:
            abort(401)
    return decorated