from functools import wraps
from flask import session, redirect,abort

def simple_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') != "stelee":
            return abort(500, "Are you trying something bad?")
        return f(*args, **kwargs)
    return decorated_function

def admin_was_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('orignal_username') != "stelee":
            return abort(500, "Are you trying something bad?")
        return f(*args, **kwargs)
    return decorated_function