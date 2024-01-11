from flask import render_template,session,redirect,flash,abort
import json

class Base():
    def __init__(self,context={}):
        self.context = context
    def execute(self,*args,**kwargs):
        pass
    def render(self, template, **kwargs):
        return render_template(template, **kwargs)
    def json(self, data):
        return {"data":json.dumps(data)}
    def message(self, mssage):
        return {"message":mssage}
    def get_session(self):
        return session
    def session_get(self,key):
        return session.get(key)
    def redirect(self,path):
        return redirect(path)
    def flash(self, msg):
        flash(msg)
    def abort(self, *args, **kwargs):
        abort(*args, **kwargs)