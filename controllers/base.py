from flask import render_template,session,redirect,flash,abort
class Base():
    def __init__(self,context={}):
        self.context = context
    def execute(self,*args,**kwargs):
        pass
    def render(self, template, **kwargs):
        return render_template(template, **kwargs)
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