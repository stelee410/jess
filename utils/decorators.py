from functools import wraps
from flask import session, redirect

def simple_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') is None:
            return redirect("/explore")
        return f(*args, **kwargs)
    return decorated_function