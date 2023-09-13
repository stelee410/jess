from flask import render_template,session
class Base():
    def __init__(self, context):
        self.context = context
    def execute(self):
        pass

    def render(self, template, **kwargs):
        return render_template(template, **kwargs)
    def get_session(self):
        return session